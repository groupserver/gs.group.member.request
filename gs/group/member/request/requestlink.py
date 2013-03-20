# coding=utf-8
from zope.cachedescriptors.property import Lazy
from gs.group.member.viewlet import MemberViewlet


class RequestLinkViewlet(MemberViewlet):
    def __init__(self, group, request, view, manager):
        MemberViewlet.__init__(self, group, request, view, manager)

    @Lazy
    def show(self):
        # Show the Request links if the user is not a member, and the
        #   group is private. Non-members cannot see secret groups, so
        #   they are not a problem.
        retval = not(self.isMember) and not(self.viewTopics)
        return retval
