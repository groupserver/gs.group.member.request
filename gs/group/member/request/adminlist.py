# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from gs.group.member.viewlet import GroupAdminViewlet
from queries import RequestQuery


class RequestMembershipListViewlet(GroupAdminViewlet):

    @Lazy
    def requestCount(self):
        rq = RequestQuery()
        retval = rq.count_current_requests(self.groupInfo.id,
                                            self.siteInfo.id)
        return retval
