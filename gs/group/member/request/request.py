# coding=utf-8
from zope.formlib import form
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base.form import GroupForm
from gs.profile.email.base.emailuser import EmailUser
from interfaces import IGSRequestMembership

class RequestForm(GroupForm):
    form_fields = form.Fields(IGSRequestMembership)
    label = _(u'Request Membership')
    pageTemplateFileName = 'browser/templates/request.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        GroupForm.__init__(self, group, request)
    
    @Lazy
    def userInfo(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        return retval

    def setUpWidgets(self, ignore_request=False):
        message = _(u'Hi there!\n\nI would like to join ') +\
            self.groupInfo.name +\
            _(u'. I think I should be allowed to become a member '
                u'because...')

        if self.userInfo.anonymous:
            fromAddr = ''
        else:
            emailUser = EmailUser(self.context, self.userInfo)
            addrs = emailUser.get_delivery_addresses()
            if addrs:
                fromAddr = addrs[0]
            else:
                fromAddr = ''

        data = {'message': message,
                'fromAddress': fromAddr}
        
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)
        
    @form.action(label=_('Request'), failure='handle_failure')
    def handle_request(self, action, data):
        self.status = u''
    
    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _(u'There was an error:')
        else:
            self.status = _(u'<p>There were errors:</p>')

