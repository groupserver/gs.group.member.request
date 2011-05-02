# coding=utf-8
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base.form import GroupForm
from interfaces import IGSRequestMembership

class RequestForm(GroupForm):
    form_fields = form.Fields(IGSRequestMembership)
    label = _(u'Request Membership')
    pageTemplateFileName = 'browser/templates/request.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        GroupForm.__init__(self, group, request)

    @form.action(label=_('Request'), failure='handle_failure')
    def handle_request(self, action, data):
        self.status = u''
    
    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _(u'There was an error:')
        else:
            self.status = _(u'<p>There were errors:</p>')

