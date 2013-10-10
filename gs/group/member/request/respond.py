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
from textwrap import TextWrapper
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from gs.group.base import GroupPage
from gs.profile.email.base import EmailUser
from .acceptor import Acceptor
from .audit import ResponseAuditor, ACCEPT, DECLINE
from .notify import NotifyAccepted, NotifyDeclined
from .queries import RequestQuery
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
                notifier = NotifyAccepted(self.context, self.request)
                for uid in accepted:
                    userInfo = createObject('groupserver.UserFromId',
                                            self.context, uid)
                    m = m + (u'<li>%s</li>\n' % acceptor.accept(userInfo))
                    notifier.notify(userInfo, self.adminInfo)
                    auditor.info(ACCEPT, userInfo)

            declined = [k.split('-decline')[0] for k in responses
                        if '-decline' in k]
            for d in declined:
                assert d not in accepted
            if declined:
                notifier = NotifyDeclined(self.context, self.request)
                for uid in declined:
                    userInfo = createObject('groupserver.UserFromId',
                                            self.context, uid)
                    m = m + (u'<li>%s</li>\n' % acceptor.decline(userInfo))
                    auditor.info(DECLINE, userInfo)
                    notifier.notify(userInfo, self.adminInfo)
            result['message'] = u'<ul>\n{0}</ul>'.format(m)

            assert 'error' in result
            assert type(result['error']) == bool
            assert 'message' in result
            assert type(result['message']) == unicode

        assert 'form' in result
        assert type(result['form']) == dict
        return result


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
