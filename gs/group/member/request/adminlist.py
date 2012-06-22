# coding=utf-8
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.member.base.viewlet import GroupAdminViewlet
from queries import RequestQuery

class RequestMembershipListViewlet(GroupAdminViewlet):
    
    @Lazy
    def requestCount(self):
        rq = RequestQuery()
        retval = rq.count_current_requests(self.groupInfo.id, 
                                            self.siteInfo.id)
        return retval

