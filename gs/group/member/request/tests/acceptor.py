# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2016 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals, print_function
from mock import (MagicMock, patch, PropertyMock)
from unittest import TestCase
from gs.group.member.request.acceptor import (Acceptor, )


class TestAcceptor(TestCase):
    '''Test the ``Acceptor`` class'''

    def user(self):
        'Get a user-info'
        retval = MagicMock()
        retval.id = 'person'
        retval.name = 'A. Person'
        return retval

    @patch.object(Acceptor, 'requestQuery', new_callable=PropertyMock)
    @patch('gs.group.member.request.acceptor.IGSJoiningUser')
    @patch('gs.group.member.request.acceptor.userInfo_to_anchor')
    @patch('gs.group.member.request.acceptor.user_member_of_group')
    def test_accept_member(self, m_u_m_o_g, m_uI_t_a, m_IGSAJU, m_rQ):
        'Test that we cope with group-members being accepted'
        m_u_m_o_g.return_value = True
        m_uI_t_a.return_value = ''
        a = Acceptor(MagicMock(), MagicMock())
        user = self.user()
        a.accept(user)

        self.assertEqual(0, m_IGSAJU.call_count)

    @patch.object(Acceptor, 'requestQuery', new_callable=PropertyMock)
    @patch('gs.group.member.request.acceptor.IGSJoiningUser')
    @patch('gs.group.member.request.acceptor.userInfo_to_anchor')
    @patch('gs.group.member.request.acceptor.user_member_of_group')
    def test_accept(self, m_u_m_o_g, m_uI_t_a, m_IGSAJU, m_rQ):
        'Test that we cope with new people being accepted as members'
        m_u_m_o_g.return_value = False
        m_uI_t_a.return_value = ''
        a = Acceptor(MagicMock(), MagicMock())
        user = self.user()
        a.accept(user)

        self.assertEqual(1, m_IGSAJU.call_count)
