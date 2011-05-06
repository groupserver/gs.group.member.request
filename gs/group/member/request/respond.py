# coding=utf-8
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from gs.group.base.page import GroupPage
from queries import RequestQuery

class Respond(GroupPage):
    def __init__(self, group, request):
        GroupPage.__init__(self, group, request)
        
    @Lazy
    def requestQuery(self):
        da = self.context.zsqlalchemy
        assert da
        retval = RequestQuery(da)
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
        if form.has_key('submitted'):
            userIds = [k.split('-respond')[0] for k in form.keys()
                if '-respond' in k]
            responses = [form['%s-respond' % k] for k in userIds]

            result['error'] = False            
            acceptedMessage = declinedMessage = u''

            accepted = [k.split('-accept')[0] for k in responses
              if '-accept' in k]
            if accepted:
                m = m + (u'Should accept request from %s' % accepted)
                # TODO

            declined = [k.split('-decline')[0] for k in responses 
                        if '-decline' in k]
            for d in declined:
                assert d not in accepted
            if declined:
                pass # TODO

            result['message'] = m

            assert result.has_key('error')
            assert type(result['error']) == bool
            assert result.has_key('message')
            assert type(result['message']) == unicode

        assert result.has_key('form')
        assert type(result['form']) == dict
        return result

class Request(object):
    def __init__(self, context, requestId, userId, message):
        self.context = context
        self.requestId = requestId
        self.userId = userId
        self.message = message

    @Lazy
    def userInfo(self):
        retval = createObject('groupserver.UserFromId', self.context, 
                                self.userId)
        assert not(retval.anonymous)
        return retval

