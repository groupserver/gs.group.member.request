# coding=utf-8
from operator import and_
import sqlalchemy as sa
from datetime import datetime
from pytz import UTC

class RequestQuery(object):
    def __init__(self, da):
        self.requestTable = da.createTable('user_group_member_request')

    def add_request(self, requestId, userId, message, siteId, groupId):
        now = datetime.now(UTC)
        i = self.requestTable.insert()
        i.execute(  request_id = requestId, user_id = userId, 
                    message = message, site_id = siteId, 
                    group_id = groupId, request_date = now)
        
    def decline_request(self, userId, groupId, adminId):
        self.update_request(userId, groupId, adminId, False)

    def accept_request(self, userId, groupId, adminId):
        self.update_request(userId, groupId, adminId, True)

    def update_request(self, userId, groupId, adminId, response):
        u = self.requestTable.update(and_(and_(
                self.requestTable.c.user_id == userId,
                self.requestTable.c.group_id == groupId),
                self.requestTable.c.response_date == None))
        now = datetime.now(UTC)
        u.execute(  responding_user_id = adminId, response_date=now, 
                    accepted = response)

    def current_requests(self, groupId, siteId):
        s = self.requestTable.select()
        s.append_whereclause(self.requestTable.c.group_id == groupId)
        s.append_whereclause(self.requestTable.c.site_id == siteId)
        s.append_whereclause(self.requestTable.c.response_date == None)
        s.order_by(sa.desc(self.requestTable.c.request_date))

        r = s.execute()
        retval = []
        seen = set()
        if r.rowcount >= 1:
            for x in r:
                if x['user_id'] not in seen:
                    seen.add(x['user_id'])
                    rd = {  'request_id':   x['request_id'],
                            'user_id':      x['user_id'],
                            'request_date': x['request_date'],
                            'message':      x['message']} 
                    retval.append(rd)
        return retval

    def count_current_requests(self, groupId, siteId):
        cols = [sa.func.count(self.requestTable.c.request_id)]
        s = sa.select(cols)
        s.append_whereclause(self.requestTable.c.group_id == groupId)
        s.append_whereclause(self.requestTable.c.site_id == siteId)
        s.append_whereclause(self.requestTable.c.response_date == None)
        
        r = s.execute()
        retval = r.scalar()
        if retval == None:
            retval = 0
        assert retval >= 0
        return retval

