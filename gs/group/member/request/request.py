# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.core import to_id, to_ascii
from gs.group.base import GroupForm
from gs.group.member.base import user_member_of_group
from gs.profile.notify.sender import MessageSender
from gs.profile.email.base.emailuser import EmailUser
from Products.GSGroupMember.groupMembersInfo import GSGroupMembersInfo
from .interfaces import IGSRequestMembership
from .queries import RequestQuery
from .audit import RequestAuditor


class RequestForm(GroupForm):
    form_fields = form.Fields(IGSRequestMembership)
    label = _('Request membership')
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
        message = _('Hi there!\n\nI would like to join ') +\
            self.groupInfo.name +\
            _('. I think I should be allowed to become a member because...')

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

    @form.action(label=_('Request'), failure='handle_failure')
    def handle_request(self, action, data):
        self.status = ''
        requestId = self.create_request_id(data['fromAddress'], data['message'])
        self.requestQuery.add_request(requestId, self.userInfo.id,
            data['message'], self.siteInfo.id, self.groupInfo.id)

        mi = GSGroupMembersInfo(self.context)
        admins = mi.groupAdmins and mi.groupAdmins or mi.siteAdmins
        for admin in admins:
            self.send_message(data['fromAddress'], admin, data['message'])

        ra = RequestAuditor(self.context, self.groupInfo, self.siteInfo)
        ra.info(self.userInfo)

        l = '<a href="%s">%s</a>. ' % (self.groupInfo.relativeURL,
                                        self.groupInfo.name)
        self.status = _('<p>You have requested membership of ') + l +\
            _('You will be contacted by the group administator when '
                'your request is considered.</p>')

    def send_message(self, fromAddress, adminInfo, message):
        sender = MessageSender(self.context, adminInfo)
        subject = _('Request to join ') + self.groupInfo.name
        newRequest = self.request
        newRequest.form['userId'] = self.userInfo.id
        newRequest.form['email'] = fromAddress
        newRequest.form['mesg'] = message
        newRequest.form['adminId'] = adminInfo.id

        txt = getMultiAdapter((self.context, newRequest),
                            name="request_message.txt")()
        html = getMultiAdapter((self.context, newRequest),
                            name="request_message.html")()
        sender.send_message(subject, txt, html, fromAddress)

        self.request.response.setHeader(to_ascii('Content-Type'),
                                            self.oldContentType)

    def create_request_id(self, fromAddress, message):
        istr = fromAddress + message + self.userInfo.id + \
            self.userInfo.name + self.groupInfo.id + self.groupInfo.name + \
            self.siteInfo.id + self.siteInfo.name
        retval = to_id(istr)
        assert retval
        return retval

    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _('There was an error:')
        else:
            self.status = _('<p>There were errors:</p>')
