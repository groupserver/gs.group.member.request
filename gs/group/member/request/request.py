# coding=utf-8
import md5
from datetime import datetime
from pytz import UTC
from zope.formlib import form
from zope.component import createObject, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import convert_int2b62
from Products.GSGroupMember.groupMembersInfo import GSGroupMembersInfo
from gs.group.base.form import GroupForm
from gs.group.member.base.utils import user_member_of_group
from gs.profile.notify.sender import MessageSender
from gs.profile.email.base.emailuser import EmailUser
from interfaces import IGSRequestMembership
from queries import RequestQuery
from audit import REQUEST, RequestAuditor

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
        retval = RequestQuery()
        return retval

    @Lazy
    def isMember(self):
        retval = user_member_of_group(self.userInfo, self.groupInfo)
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

        data = {'message': message, 'fromAddress': fromAddr}
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
        
        mi = GSGroupMembersInfo(self.context)
        admins = mi.groupAdmins and mi.groupAdmins or mi.siteAdmins
        for admin in admins:
            self.send_message(data['fromAddress'], admin, data['message'])

        ra = RequestAuditor(self.context, self.groupInfo, self.siteInfo)
        ra.info(self.userInfo)

        l = '<a href="%s">%s</a>. ' % (self.groupInfo.url, 
                                        self.groupInfo.name)
        self.status = _(u'You have requested membership of ') + l +\
            _(u'You will be contacted by the group administator when '\
                u'your request is considered.')

    def send_message(self, fromAddress, adminInfo, message):
        sender = MessageSender(self.context, adminInfo)
        subject = _(u'Request to Join ') + self.groupInfo.name
        newRequest = self.request
        newRequest.form['userId'] = self.userInfo.id
        newRequest.form['email'] = fromAddress
        newRequest.form['mesg'] = message
        newRequest.form['adminId'] = adminInfo.id
        txt = getMultiAdapter((self.context, newRequest),
                            name="request_message.txt")()
        html = getMultiAdapter((self.context, newRequest),
                            name="request_message.html")()
        sender.send_message(subject, txt, html, fromAddress)
        
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

    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _(u'There was an error:')
        else:
            self.status = _(u'<p>There were errors:</p>')

