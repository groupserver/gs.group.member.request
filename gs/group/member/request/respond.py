# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import formataddr
from textwrap import TextWrapper
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from gs.group.base.page import GroupPage
from gs.profile.email.base.emailuser import EmailUser
from Products.XWFCore.XWFUtils import get_support_email
from .queries import RequestQuery
from .acceptor import Acceptor
from .audit import ResponseAuditor, ACCEPT, DECLINE
utf8 = 'utf-8'


class Respond(GroupPage):
    def __init__(self, group, request):
        GroupPage.__init__(self, group, request)

    @Lazy
    def requestQuery(self):
        retval = RequestQuery()
        return retval

    @Lazy
    def requests(self):
        rd = self.requestQuery.current_requests(self.groupInfo.id,
                                                self.siteInfo.id)
        retval = [Request(self.context, r['request_id'], r['user_id'],
                            r['message'])
                    for r in rd]
        assert type(retval) == list
        return retval

    @Lazy
    def adminInfo(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        assert not(retval.anonymous)
        return retval

    def process_form(self):
        '''Process the forms in the page.

        This method uses the "submitted" pattern that is used for the
        XForms impementation on GroupServer.
          * The method is called whenever the page is loaded by
            tal:define="result view/process_form".
          * The submitted form is checked for the hidden "submitted" field.
            This field is only returned if the user submitted the form,
            not when the page is loaded for the first time.
            - If the field is present, then the form is processed.
            - If the field is absent, then the method re  turns.

        RETURNS
            A "result" dictionary, that at-least contains the form that
            was submitted'''
        # TOOD: I could probabily implement this page as a list of
        #       choice fields, and a custom widget to display the data
        #       about the membership request. However, it is easier to
        #       reuse an old pattern than figure out how to get formlib
        #       to behave.
        form = self.context.REQUEST.form
        result = {}
        result['form'] = form
        m = u''
        if 'submitted' in form:
            userIds = [k.split('-respond')[0] for k in form.keys()
                if '-respond' in k]
            responses = [form['%s-respond' % k] for k in userIds]

            result['error'] = False

            acceptor = Acceptor(self.adminInfo, self.groupInfo)
            auditor = ResponseAuditor(self.context, self.adminInfo,
                                        self.groupInfo, self.siteInfo)

            accepted = [k.split('-accept')[0] for k in responses
              if '-accept' in k]
            if accepted:
                for uid in accepted:
                    userInfo = createObject('groupserver.UserFromId',
                                            self.context, uid)
                    m = m + (u'<li>%s</li>\n' % acceptor.accept(userInfo))
                    auditor.info(ACCEPT, userInfo)

            declined = [k.split('-decline')[0] for k in responses
                        if '-decline' in k]
            for d in declined:
                assert d not in accepted
            if declined:
                for uid in declined:
                    userInfo = createObject('groupserver.UserFromId',
                                            self.context, uid)
                    m = m + (u'<li>%s</li>\n' % acceptor.decline(userInfo))
                    auditor.info(DECLINE, userInfo)
                    self.create_decline_message(userInfo)
            result['message'] = u'<ul>\n%s</ul>' % m

            assert 'error' in result
            assert type(result['error']) == bool
            assert 'message' in result
            assert type(result['message']) == unicode

        assert 'form' in result
        assert type(result['form']) == dict
        return result

    def create_decline_message(self, userInfo):
        container = MIMEMultipart('alternative')
        subject = _(u'Request to Join ') + self.groupInfo.name
        container['Subject'] = str(Header(subject, utf8))
        supportAddress = get_support_email(self.context, self.siteInfo.id)
        fromAddr = formataddr(('%s Support' % self.siteInfo.name,
                                supportAddress))
        container['From'] = fromAddr
        # TODO: To
        toAddr = formataddr(('You', 'mpj17@groupsense.net'))
        container['To'] = toAddr

        newRequest = self.request
        newRequest.form['adminId'] = self.adminInfo.id
        newRequest.form['userId'] = userInfo.id
        newRequest.form['email'] = ''
        newRequest.form['mesg'] = ''

        t = getMultiAdapter((self.context, newRequest),
                            name="decline_message.txt")()
        txt = MIMEText(t.encode(utf8), 'plain', utf8)
        container.attach(txt)

        h = getMultiAdapter((self.context, newRequest),
                            name="decline_message.html")()
        html = MIMEText(h.encode(utf8), 'html', utf8)
        container.attach(html)

        retval = container.as_string()
        print retval
        return retval


class Request(object):
    email_wrapper = TextWrapper(width=72, expand_tabs=False,
                        replace_whitespace=False, break_on_hyphens=False,
                        break_long_words=False)

    def __init__(self, context, requestId, userId, message):
        self.context = context
        self.requestId = requestId
        self.userId = userId
        self.message = self.email_wrapper.fill(message)

    @Lazy
    def userInfo(self):
        retval = createObject('groupserver.UserFromId', self.context,
                                self.userId)
        assert not(retval.anonymous)
        return retval

    @Lazy
    def email(self):
        # Note: This is not quite right, as the member could use a
        #   different email address to send the request to the one that
        #   is returned here.
        eu = EmailUser(self.context, self.userInfo)
        addrs = eu.get_verified_addresses()
        m = '%s (%s) has no verified email address' % \
            (self.userInfo.name, self.userInfo.id)
        assert len(addrs) > 0, m
        retval = addrs[0]
        return retval
