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
from __future__ import absolute_import
from zope.cachedescriptors.property import Lazy
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from gs.group.member.base import user_member_of_group
from gs.group.member.join.interfaces import IGSJoiningUser
from .queries import RequestQuery


class Acceptor(object):
    def __init__(self, adminInfo, groupInfo):
        self.adminInfo = adminInfo
        self.groupInfo = groupInfo

    @Lazy
    def requestQuery(self):
        retval = RequestQuery()
        return retval

    def accept(self, userInfo):
        self.requestQuery.accept_request(userInfo.id, self.groupInfo.id,
                                            self.adminInfo.id)
        if user_member_of_group(userInfo, self.groupInfo):
            retval = u'%s is already a member of the group, so '\
                u'the request was ignored.' % userInfo_to_anchor(userInfo)
        else:
            joiningUser = IGSJoiningUser(userInfo)
            joiningUser.join(self.groupInfo)
            retval = u'Accepted the request from %s' % \
                            userInfo_to_anchor(userInfo)
        return retval

    def decline(self, userInfo):
        self.requestQuery.decline_request(userInfo.id, self.groupInfo.id,
            self.adminInfo.id)
        return u'Declined the request from %s' % userInfo_to_anchor(userInfo)
