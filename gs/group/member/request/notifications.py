# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
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
from urllib import quote
from zope.cachedescriptors.property import Lazy
from gs.content.email.base import GroupEmail
from Products.GSGroup.interfaces import IGSMailingListInfo
UTF8 = 'utf-8'


class AcceptedMessage(GroupEmail):

    @Lazy
    def supportEmail(self):
        m = u'Hi!\n\nI was accepted into the group {0}\n    {1}\nand...'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        sub = quote('Membership accepted')
        r = 'mailto:{0}?Subject={1}&body={2}'
        retval = r.format(self.siteInfo.get_support_email(), sub,
                            quote(msg.encode(UTF8)))
        return retval

    @Lazy
    def email(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval


class AcceptedMessageText(AcceptedMessage):

    def __init__(self, context, request):
        super(AcceptedMessageText, self).__init__(context, request)
        response = request.response
        response.setHeader("Content-Type", 'text/plain; charset=UTF-8')
        filename = 'welcome-to-%s.txt' % self.groupInfo.name
        response.setHeader('Content-Disposition',
                            'inline; filename="%s"' % filename)


class DeclinedMessage(GroupEmail):

    @Lazy
    def supportEmail(self):
        m = u'Hi!\n\nI was declined membership of the group {0}\n    '\
            u'{1}\nand...'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        sub = quote('Membership declined')
        r = 'mailto:{0}?Subject={1}&body={2}'
        retval = r.format(self.siteInfo.get_support_email(), sub,
                            quote(msg.encode(UTF8)))
        return retval


class DeclinedMessageText(AcceptedMessage):

    def __init__(self, context, request):
        super(DeclinedMessageText, self).__init__(context, request)
        response = request.response
        response.setHeader("Content-Type", 'text/plain; charset=UTF-8')
        filename = 'welcome-to-%s.txt' % self.groupInfo.name
        response.setHeader('Content-Disposition',
                            'inline; filename="%s"' % filename)
