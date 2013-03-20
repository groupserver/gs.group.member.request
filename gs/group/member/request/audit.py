# coding=utf-8
from pytz import UTC
from datetime import datetime
from zope.component.interfaces import IFactory
from zope.cachedescriptors.property import Lazy
from zope.interface import implements, implementedBy
from Products.XWFCore.XWFUtils import munge_date
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.GSAuditTrail.utils import event_id_from_data

SUBSYSTEM = 'gs.group.member.request'
import logging
log = logging.getLogger(SUBSYSTEM)

UNKNOWN = '0'  # Unknown is always "0"
REQUEST = '1'
ACCEPT = '2'
DECLINE = '3'


class AuditFactory(object):
    """A Factory for membership-request events.
    """
    implements(IFactory)

    title = u'GroupServer Membership Request Audit Event Factory'
    description = u'Creates a GroupServer event auditor for request events'

    def __call__(self, context, event_id, code, date,
        userInfo, instanceUserInfo, siteInfo, groupInfo,
        instanceDatum='', supplementaryDatum='', subsystem=''):
        """Create an event
        """
        assert subsystem == SUBSYSTEM, 'Subsystems do not match'

        if code == REQUEST:
            event = RequestEvent(context, event_id, date,
                        instanceUserInfo, siteInfo, groupInfo)
        elif code == ACCEPT:
            event = AcceptEvent(context, event_id, date, userInfo,
                        instanceUserInfo, siteInfo, groupInfo)
        elif code == DECLINE:
            event = DeclineEvent(context, event_id, date, userInfo,
                        instanceUserInfo, siteInfo, groupInfo)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
              userInfo, instanceUserInfo, siteInfo, groupInfo,
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


class RequestEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a site.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, instanceUserInfo,
                  siteInfo, groupInfo):
        """ Create a request event
        """
        BasicAuditEvent.__init__(self, context, id, REQUEST, d, None,
          instanceUserInfo, siteInfo, groupInfo, None, None,
          SUBSYSTEM)

    def __str__(self):
        retval = u'%s (%s) requested membership of the group %s (%s).' %\
           (self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.groupInfo.name, self.groupInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event groupserver-group-member-request-%s' %\
          self.code
        retval = u'<span class="%s">Requested membership of %s</span>' %\
          (cssClass, self.groupInfo.name)

        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval


class AcceptEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a site.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                  siteInfo, groupInfo):
        """ Create a request event
        """
        BasicAuditEvent.__init__(self, context, id, ACCEPT, d, userInfo,
          instanceUserInfo, siteInfo, groupInfo, None, None,
          SUBSYSTEM)

    def __str__(self):
        retval = u'%s (%s) accepted the request from %s (%s) to join '\
            u'the group %s (%s).' %\
           (self.userInfo.name, self.userInfo.id,
            self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.groupInfo.name, self.groupInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event groupserver-group-member-accept-%s' %\
          self.code
        retval = u'<span class="%s">%s accepted the request to join '\
            u'%s</span>' %\
          (cssClass, self.userInfo.name, self.groupInfo.name)

        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval


class DeclineEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person being declined a
    request to join a group
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                  siteInfo, groupInfo):
        """ Create a request event
        """
        BasicAuditEvent.__init__(self, context, id, DECLINE, d, userInfo,
          instanceUserInfo, siteInfo, groupInfo, None, None,
          SUBSYSTEM)

    def __str__(self):
        retval = u'%s (%s) declined the request from %s (%s) to join '\
            u'the group %s (%s).' %\
           (self.userInfo.name, self.userInfo.id,
            self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.groupInfo.name, self.groupInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event groupserver-group-member-decline-%s' %\
          self.code
        retval = u'<span class="%s">%s declined the request to join '\
            u'%s</span>' %\
          (cssClass, self.userInfo.name, self.groupInfo.name)

        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
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
        eventId = event_id_from_data(instanceUser, instanceUser,
            self.siteInfo, REQUEST, '',
            '%s-%s' % (self.groupInfo.name, self.groupInfo.id))
        d = datetime.now(UTC)
        f = AuditFactory()
        e = f(self.context, eventId, REQUEST, d,
                instanceUser, instanceUser,
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
        eventId = event_id_from_data(self.userInfo,
            instanceUserInfo, self.siteInfo, code, '',
            '%s-%s' % (self.groupInfo.name, self.groupInfo.id))
        e = self.factory(self.context, eventId, code, d,
                        self.userInfo, instanceUserInfo,
                        self.siteInfo, self.groupInfo, '', '', SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e
