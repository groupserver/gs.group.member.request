# coding=utf-8
from zope.interface import Interface
from zope.schema import Text

class IGSRequestMembership(Interface):
    message = Text(title=u'Message',
        description=u'The message you want to send to the administrator '
            u'explaining why you should be a member of the group.',
        required=True)

