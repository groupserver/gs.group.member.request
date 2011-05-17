# coding=utf-8
from cgi import escape
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from gs.group.base.page import GroupPage

class RequestMessage(GroupPage):
    def __init__(self, group, request):
        GroupPage.__init__(self, group, request)
        self.userId = request.form['userId']
        self.adminId = request.form['adminId']
        self.email = request.form['email']
        self.mesg  = request.form['mesg']

    @Lazy    
    def userInfo(self):
        assert self.userId
        retval = createObject('groupserver.UserFromId', self.context, 
                                self.userId)
        return retval

    @Lazy
    def adminInfo(self):
        assert self.adminId
        retval = createObject('groupserver.UserFromId', self.context, 
                                self.adminId)
        return retval

    @Lazy
    def message(self):
        r = escape(self.mesg)
        retval = u'<p>%s</p>' %\
            r.replace(u'\n\n', u'</p><p>').replace(u'\n',u'<br/>')
        return retval

