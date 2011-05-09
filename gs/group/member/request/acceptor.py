# coding=utf-8
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
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

    def accept(self, userId):
        userInfo = createObject('groupserver.UserFromId', 
                                    self.groupInfo.groupObj, userId)
        joiningUser = IGSJoiningUser(userInfo)
        joiningUser.join(self.groupInfo)
        self.requestQuery.accept_request(userInfo.id, self.groupInfo.id,
            self.adminInfo.id)
        # TODO Audit

    def decline(self, userId):
        self.requestQuery.decline_request(userId, self.groupInfo.id,
            self.adminInfo.id)        
        # TODO Audit

