# coding=utf-8
import md5
from datetime import datetime
from pytz import UTC
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
from Products.XWFCore.XWFUtils import convert_int2b62
from gs.group.base.form import GroupForm
from gs.profile.email.base.emailuser import EmailUser
from interfaces import IGSRequestMembership
from queries import RequestQuery
from audit import REQUEST, RequestAuditor
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

    @Lazy
    def requestQuery(self):
        da = self.context.zsqlalchemy
        assert da
        retval = RequestQuery(da)
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
        requestId = self.create_request_id(data['fromAddress'], data['message'])
        self.requestQuery.add_request(requestId, self.userInfo.id, 
            data['message'], self.siteInfo.id, self.groupInfo.id)
        msg  = self.create_message(data['fromAddress'], data['message'])

        ra = RequestAuditor(self.context, self.groupInfo, self.siteInfo)
        ra.info(self.userInfo)

        l = '<a href="%s">%s</a>. ' % (self.groupInfo.url, 
                                        self.groupInfo.name)
        self.status = _(u'You have requested membership of ') + l +\
            _(u'You will be contacted by the group administator when '\
                u'your request is considered.')


    def create_request_id(self, fromAddress, message):
        istr = fromAddress + message + self.userInfo.id + \
            str(datetime.now(UTC)) + self.userInfo.name + \
            self.groupInfo.id + self.groupInfo.name + \
            self.siteInfo.id + self.siteInfo.name
        inum = long(md5.new(istr).hexdigest(), 16)
        retval = str(convert_int2b62(inum))
        assert retval
        assert type(retval) == str
        return retval

    def create_message(self, fromAddress, message):
        container = MIMEMultipart('alternative')
        subject = _(u'Request to Join ') + self.groupInfo.name
        container['Subject'] = str(Header(subject, utf8))
        fromAddr = formataddr((self.userInfo.name, fromAddress))
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
        newRequest.form['mesg'] = message
        
        t = getMultiAdapter((self.context, newRequest),
                            name="request_message.txt")()
        txt = MIMEText(t.encode(utf8), 'plain', utf8)   
        container.attach(txt)

        h = getMultiAdapter((self.context, newRequest),
                            name="request_message.html")()
        html = MIMEText(h.encode(utf8), 'html', utf8)   
        container.attach(html)

        retval = container.as_string()
        print retval
        return retval

    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _(u'There was an error:')
        else:
            self.status = _(u'<p>There were errors:</p>')

