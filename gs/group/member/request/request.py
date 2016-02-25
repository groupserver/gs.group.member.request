# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013, 2014, 2016 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals, print_function
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.core import to_id, to_ascii
from gs.group.base import GroupForm
from gs.group.member.base import (user_member_of_group, GroupAdminMembers, SiteAdminMembers, )
from gs.profile.notify.sender import MessageSender
from gs.profile.email.base.emailuser import EmailUser
from .interfaces import IGSRequestMembership
from .queries import RequestQuery
from .audit import RequestAuditor
from . import GSMessageFactory as _


class RequestForm(GroupForm):
    form_fields = form.Fields(IGSRequestMembership)
    label = _('request-h', 'Request membership')
    pageTemplateFileName = 'browser/templates/request.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        super(RequestForm, self).__init__(group, request)
        h = request.response.getHeader('Content-Type')
        self.oldContentType = to_ascii(h if h else 'text/html')

    @Lazy
    def userInfo(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        return retval

    @Lazy
    def requestQuery(self):
        retval = RequestQuery()
        return retval

    @Lazy
    def isMember(self):
        retval = user_member_of_group(self.userInfo, self.groupInfo)
        return retval

    def setUpWidgets(self, ignore_request=False):
        message = _('request-message-default',
                    'Hello,\n\nI would like to join ${groupName}. I think I should be allowed to '
                    'become a member because...',
                    mapping={'groupName': self.groupInfo.name})

        if self.userInfo.anonymous:
            fromAddr = ''
        else:
            emailUser = EmailUser(self.context, self.userInfo)
            addrs = emailUser.get_delivery_addresses()
            if addrs:
                fromAddr = addrs[0]
            else:
                fromAddr = ''

        data = {'message': message, 'fromAddress': fromAddr}
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @Lazy
    def admins(self):
        retval = GroupAdminMembers(self.context)
        if len(retval) == 0:
            retval = SiteAdminMembers(self.context)
            if len(retval) == 0:
                retval = self.siteInfo.site_admins
                if len(retval) == 0:
                    m = 'The group {0} ({1}) and the site {2} ({3}) lacks any administrators.'
                    msg = m.format(self.groupInfo.name, self.groupInfo.id,
                                   self.siteInfo.name, self.siteInfo.id)
                    raise ValueError(msg)
        return retval

    @form.action(name='request', label=_('request-button', 'Request'), failure='handle_failure')
    def handle_request(self, action, data):
        self.status = ''
        requestId = self.create_request_id(data['fromAddress'], data['message'])
        self.requestQuery.add_request(requestId, self.userInfo.id, data['message'],
                                      self.siteInfo.id, self.groupInfo.id)

        for admin in self.admins:
            self.send_message(data['fromAddress'], admin, data['message'])

        ra = RequestAuditor(self.context, self.groupInfo, self.siteInfo)
        ra.info(self.userInfo)

        l = '<a href="%s">%s</a>. ' % (self.groupInfo.relativeURL, self.groupInfo.name)
        self.status = _('request-feedback',
                        '<p>You have requested membership of ${groupName}. You will be '
                        'contacted by the group administator when your request is considered.</p>',
                        mapping={'groupName': l})

    def send_message(self, fromAddress, adminInfo, message):
        sender = MessageSender(self.context, adminInfo)
        subject = _('request-admin-message-subject',  'Request to join ${groupName}',
                    mapping={'groupName': self.groupInfo.name})
        newRequest = self.request
        newRequest.form['userId'] = self.userInfo.id
        newRequest.form['email'] = fromAddress
        newRequest.form['mesg'] = message
        newRequest.form['adminId'] = adminInfo.id

        txt = getMultiAdapter((self.context, newRequest), name="request_message.txt")()
        html = getMultiAdapter((self.context, newRequest), name="request_message.html")()
        sender.send_message(subject, txt, html, fromAddress)

        self.request.response.setHeader(b'Content-Type', self.oldContentType)

    def create_request_id(self, fromAddress, message):
        istr = fromAddress + message + self.userInfo.id + \
            self.userInfo.name + self.groupInfo.id + self.groupInfo.name + \
            self.siteInfo.id + self.siteInfo.name
        retval = to_id(istr)
        assert retval
        return retval

    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _('request-error', 'There was an error:')
        else:
            self.status = _('request-errors', '<p>There were errors:</p>')
