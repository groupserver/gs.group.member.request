# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import unicode_literals
from datetime import datetime
import logging
SUBSYSTEM = 'gs.group.member.request'
log = logging.getLogger(SUBSYSTEM)
from pytz import UTC
from zope.component.interfaces import IFactory
from zope.cachedescriptors.property import Lazy
from zope.interface import implements, implementedBy
from Products.XWFCore.XWFUtils import munge_date
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.GSAuditTrail.utils import event_id_from_data
UNKNOWN = '0'  # Unknown is always "0"
REQUEST = '1'
ACCEPT = '2'
DECLINE = '3'


class AuditFactory(object):
    """A Factory for membership-request events.
    """
    implements(IFactory)

    title = 'GroupServer Membership Request Audit Event Factory'
    description = 'Creates a GroupServer event auditor for request events'

    def __call__(self, context, event_id, code, date, userInfo,
                 instanceUserInfo, siteInfo, groupInfo, instanceDatum='',
                 supplementaryDatum='', subsystem=''):
        """Create an event"""
        assert subsystem == SUBSYSTEM, 'Subsystems do not match'

        if code == REQUEST:
            event = RequestEvent(context, event_id, date, instanceUserInfo,
                                 siteInfo, groupInfo)
        elif code == ACCEPT:
            event = AcceptEvent(context, event_id, date, userInfo,
                                instanceUserInfo, siteInfo, groupInfo)
        elif code == DECLINE:
            event = DeclineEvent(context, event_id, date, userInfo,
                                 instanceUserInfo, siteInfo, groupInfo)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
                                    userInfo, instanceUserInfo, siteInfo,
                                    groupInfo, instanceDatum,
                                    supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


class RequestEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a site.
    '''
    implements(IAuditEvent)

    def __init__(self, context, eventId, d, instanceUserInfo, siteInfo,
                 groupInfo):
        super(RequestEvent, self).__init__(
            context, eventId, REQUEST, d, None, instanceUserInfo, siteInfo,
            groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        retval = '%s (%s) requested membership of the group %s (%s).' %\
            (self.instanceUserInfo.name, self.instanceUserInfo.id,
             self.groupInfo.name, self.groupInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-request-%s' % \
            self.code
        retval = '<span class="%s">Requested membership of %s</span>' %\
            (cssClass, self.groupInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class AcceptEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a site.
    '''
    implements(IAuditEvent)

    def __init__(self, context, eventId, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo):
        super(AcceptEvent, self).__init__(
            context, eventId, ACCEPT, d, userInfo, instanceUserInfo,
            siteInfo, groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        retval = '%s (%s) accepted the request from %s (%s) to join '\
            'the group %s (%s).' %\
            (self.userInfo.name, self.userInfo.id,
             self.instanceUserInfo.name, self.instanceUserInfo.id,
             self.groupInfo.name, self.groupInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-accept-%s' % \
            self.code
        retval = '<span class="%s">%s accepted the request to join '\
            '%s</span>' % (cssClass, self.userInfo.name,
                           self.groupInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class DeclineEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person being declined a
    request to join a group
    '''
    implements(IAuditEvent)

    def __init__(self, context, eventId, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo):
        super(DeclineEvent, self).__init__(
            context, eventId, DECLINE, d, userInfo, instanceUserInfo,
            siteInfo, groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        retval = '%s (%s) declined the request from %s (%s) to join '\
            'the group %s (%s).' %\
            (self.userInfo.name, self.userInfo.id,
             self.instanceUserInfo.name, self.instanceUserInfo.id,
             self.groupInfo.name, self.groupInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-decline-%s' % \
            self.code
        retval = '<span class="%s">%s declined the request to join '\
            '%s</span>' %\
            (cssClass, self.userInfo.name, self.groupInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class RequestAuditor(object):
    def __init__(self, context, groupInfo, siteInfo):
        self.context = context
        self.groupInfo = groupInfo
        self.siteInfo = siteInfo

    @Lazy
    def queries(self):
        retval = AuditQuery()
        return retval

    def info(self, instanceUser):
        mushForId = '%s-%s' % (self.groupInfo.name, self.groupInfo.id)
        eventId = event_id_from_data(
            instanceUser, instanceUser, self.siteInfo, REQUEST, '',
            mushForId.encode('ascii', 'xmlcharrefreplace'))
        d = datetime.now(UTC)
        f = AuditFactory()
        e = f(self.context, eventId, REQUEST, d, instanceUser, instanceUser,
              self.siteInfo, self.groupInfo, '', '', SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e


class ResponseAuditor(object):
    def __init__(self, context, userInfo, groupInfo, siteInfo):
        self.context = context
        self.userInfo = userInfo
        self.groupInfo = groupInfo
        self.siteInfo = siteInfo
        self.factory = AuditFactory()

    @Lazy
    def queries(self):
        retval = AuditQuery()
        return retval

    def info(self, code, instanceUserInfo):
        d = datetime.now(UTC)
        mushForId = '%s-%s' % (self.groupInfo.name, self.groupInfo.id)
        eventId = event_id_from_data(
            self.userInfo, instanceUserInfo,  self.siteInfo, code, '',
            mushForId.encode('ascii', 'xmlcharrefreplace'))
        e = self.factory(self.context, eventId, code, d, self.userInfo,
                         instanceUserInfo, self.siteInfo, self.groupInfo,
                         '', '', SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e
