# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import unicode_literals
from zope.interface import Interface
from zope.schema import Text, Choice


class IGSRequestMembership(Interface):
    fromAddress = Choice(title='From',
        description='The email address that you want in the "From" '
          'line in the email you send.',
        vocabulary='EmailAddressesForLoggedInUser',
        required=True)

    message = Text(title='Message',
        description='The message you want to send to the administrator '
            'explaining why you should be a member of the group.',
        required=True)
