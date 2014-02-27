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
from __future__ import unicode_literals
from cgi import escape
from urllib import urlencode
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from gs.content.email.base import GroupEmail, TextMixin


class RequestMessage(GroupEmail):

    def __init__(self, group, request):
        super(RequestMessage, self).__init__(group, request)
        assert 'userId' in request.form, 'No userId'
        self.userId = request.form['userId']
        assert 'adminId' in request.form, 'No adminId'
        self.adminId = request.form['adminId']
        assert 'email' in request.form, 'No email'
        self.email = request.form['email']
        assert 'mesg' in request.form, 'No mesg'
        self.mesg = request.form['mesg']

    @Lazy
    def userInfo(self):
        assert self.userId
        retval = createObject('groupserver.UserFromId', self.context,
                                self.userId)
        return retval

    @Lazy
    def adminInfo(self):
        assert self.adminId
        retval = createObject('groupserver.UserFromId', self.context,
                                self.adminId)
        return retval

    @Lazy
    def message(self):
        r = escape(self.mesg)
        retval = '<p>%s</p>' %\
            r.replace('\n\n', '</p><p>').replace('\n', '<br/>')
        return retval

    @Lazy
    def support(self):
        s = 'Membership request'
        m = 'Hi!\n\nI received a request from {0} to join the group '\
            '{1}\n    {2}\nand...'
        msg = m.format(self.userInfo.name, self.groupInfo.name,
                        self.groupInfo.url)
        data = {'Subject': s,
                  'body': msg.encode('UTF-8'), }

        retval = 'mailto:{0}?{1}'.format(self.siteInfo.get_support_email(),
                                        urlencode(data))
        return retval


class RequestMessageText(RequestMessage, TextMixin):

    def __init__(self, context, request):
        super(RequestMessageText, self).__init__(context, request)
        filename = 'request-message-{0}.txt'.format(self.groupInfo.id)
        self.set_header(filename)
