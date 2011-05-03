# coding=utf-8
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from gs.group.base.page import GroupPage

class RequestMessage(GroupPage):
    def __init__(self, group, request):
        GroupPage.__init__(self, group, request)
        print 'Here 1'
        self.userId = request.form['userId']
        print 'Here 2'
        self.adminId = request.form['adminId']
        print 'Here 3'
        self.email = request.form['email']
        print 'Here 4'
        self.mesg  = request.form['mesg']
        print 'Here 5'

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
    def mailto(self):
        assert self.email
        s = _(u'Your Request to Join ') + self.groupInfo.name
        retval = 'mailto:%s?Subject=%s' % (self.email, s)
        return retval

