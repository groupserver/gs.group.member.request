# coding=utf-8
from zope.interface import Interface
from zope.schema import Text, Choice

class IGSRequestMembership(Interface):
    fromAddress = Choice(title=u'From',
      description=u'The email address that you want in the "From" '\
        u'line in the email you send.',
      vocabulary = 'EmailAddressesForLoggedInUser',
      required=True)

    message = Text(title=u'Message',
        description=u'The message you want to send to the administrator '
            u'explaining why you should be a member of the group.',
        required=True)

