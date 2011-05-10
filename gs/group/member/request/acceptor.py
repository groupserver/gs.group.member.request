# coding=utf-8
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from gs.group.member.join.interfaces import IGSJoiningUser
from queries import RequestQuery

class Acceptor(object):
    def __init__(self, adminInfo, groupInfo):
        self.adminInfo = adminInfo
        self.groupInfo = groupInfo

    @Lazy
    def requestQuery(self):
        da = self.groupInfo.groupObj.zsqlalchemy
        assert da
        retval = RequestQuery(da)
        return retval

    def accept(self, userInfo):
        joiningUser = IGSJoiningUser(userInfo)
        joiningUser.join(self.groupInfo)
        self.requestQuery.accept_request(userInfo.id, self.groupInfo.id,
            self.adminInfo.id)
        return u'Accepted the request from %s' % userInfo_to_anchor(userInfo)

    def decline(self, userInfo):
        self.requestQuery.decline_request(userInfo.id, self.groupInfo.id,
            self.adminInfo.id)        
        return u'Declined the request from %s' % userInfo_to_anchor(userInfo)

