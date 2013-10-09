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
from cgi import escape
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from gs.group.base import GroupPage


class RequestMessage(GroupPage):
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
        retval = u'<p>%s</p>' %\
            r.replace(u'\n\n', u'</p><p>').replace(u'\n', u'<br/>')
        return retval
