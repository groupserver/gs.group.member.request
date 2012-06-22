# coding=utf-8
from operator import and_
import sqlalchemy as sa
from datetime import datetime
from pytz import UTC
from gs.database import getTable, getSession
from zope.sqlalchemy import mark_changed

class RequestQuery(object):
    def __init__(self):
        self.requestTable = getTable('user_group_member_request')

    def add_request(self, requestId, userId, message, siteId, groupId):
        now = datetime.now(UTC)
        i = self.requestTable.insert()
        session.execute(i, params={"request_id": requestId, "user_id": userId, 
                                   "message": message, "site_id": siteId, 
                                   "group_id": groupId, "request_date": now})
        mark_changed(session)
        
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
        session = getSession() 
        session.execute(u, params={'responding_user_id': adminId,
                                   'response_date': now, 
                                   'accepted': response})
        mark_changed(session)

    def current_requests(self, groupId, siteId):
        s = self.requestTable.select(
                    order_by=sa.desc(self.requestTable.c.request_date))
        s.append_whereclause(self.requestTable.c.group_id == groupId)
        s.append_whereclause(self.requestTable.c.site_id == siteId)
        s.append_whereclause(self.requestTable.c.response_date == None)
        
        session = getSession()
        r = session.execute(s)
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
        
        session = getSession()
        r = session.execute(s)
        retval = r.scalar()
        if retval == None:
            retval = 0
        assert retval >= 0
        return retval

