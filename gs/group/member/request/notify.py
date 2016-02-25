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
from zope.component import createObject, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from gs.core import to_ascii
from gs.profile.notify.sender import MessageSender
UTF8 = 'utf-8'


class NotifyAccepted(object):
    textTemplateName = 'gs-group-member-request-accepted.txt'
    htmlTemplateName = 'gs-group-member-request-accepted.html'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        h = self.request.response.getHeader('Content-Type')
        self.oldContentType = to_ascii(h if h else 'text/html')

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        assert retval, 'Could not create the GroupInfo from %s' % self.context
        return retval

    @Lazy
    def textTemplate(self):
        retval = getMultiAdapter((self.context, self.request), name=self.textTemplateName)
        assert retval
        return retval

    @Lazy
    def htmlTemplate(self):
        retval = getMultiAdapter((self.context, self.request), name=self.htmlTemplateName)
        assert retval
        return retval

    def notify(self, userInfo, adminInfo):
        subject = ('Welcome to %s' % (self.groupInfo.name).encode(UTF8))
        text = self.textTemplate(userInfo=userInfo, adminInfo=adminInfo)
        html = self.htmlTemplate(userInfo=userInfo, adminInfo=adminInfo)
        ms = MessageSender(self.context, userInfo)
        ms.send_message(subject, text, html)
        self.request.response.setHeader(b'Content-Type', self.oldContentType)


class NotifyDeclined(NotifyAccepted):
    textTemplateName = 'gs-group-member-request-declined.txt'
    htmlTemplateName = 'gs-group-member-request-declined.html'
