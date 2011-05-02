# coding=utf-8
from gs.group.base.page import GroupPage

class RequestMessage(GroupPage):
    def __init__(self, group, request):
        GroupPage.__init__(self, group, request)

