# coding=utf-8
from email.Message import Message
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import formataddr
from zope.formlib import form
from zope.component import createObject, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base.form import GroupForm
from gs.profile.email.base.emailuser import EmailUser
from interfaces import IGSRequestMembership
utf8 = 'utf-8'

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

        container = MIMEMultipart('alternative')
        subject = _(u'Request to Join ') + self.groupInfo.name
        container['Subject'] = str(Header(subject, utf8))
        fromAddr = formataddr((self.userInfo.name, data['fromAddress']))
        container['From'] = fromAddr
        # TODO: To
        toAddr = formataddr(('You', 'mpj17@groupsense.net'))
        container['To'] = toAddr
        # --=mpj17=-- check where bounces should go
        groupAddr = formataddr(('The Group', 'mpj17@groupsense.net'))
        container['Reply-to'] = groupAddr 

        newRequest = self.request
        newRequest.form['adminId'] = '6wqOHuEKAVClbmHaIuqYWF'
        newRequest.form['userId'] = self.userInfo.id
        newRequest.form['email'] = 'mpj17@groupsense.net'
        newRequest.form['mesg'] = data['message']
        
        t = getMultiAdapter((self.context, newRequest),
                            name="request_message.txt")()
        txt = MIMEText(t.encode(utf8), 'plain', utf8)   
        container.attach(txt)

        h = getMultiAdapter((self.context, newRequest),
                            name="request_message.html")()
        html = MIMEText(h.encode(utf8), 'html', utf8)   
        container.attach(html)
        
        print container.as_string()

    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _(u'There was an error:')
        else:
            self.status = _(u'<p>There were errors:</p>')

