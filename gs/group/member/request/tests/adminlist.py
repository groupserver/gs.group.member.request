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
from gs.group.member.request.adminlist import (RequestMembershipListViewlet, )


class TestRequestMembershipListViewlet(TestCase):
    '''Test the ``RequestMembershipListViewlet`` class'''

    @patch.object(RequestMembershipListViewlet, 'requestCount', new_callable=PropertyMock)
    @patch('gs.group.member.request.adminlist.GroupAdminViewlet.show', new_callable=PropertyMock)
    def test_show_not_admin(self, m_GAV_s, m_rC):
        'Test that we are hidden for normal users'
        m_GAV_s.return_value = False
        v = RequestMembershipListViewlet(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        r = v.show

        self.assertFalse(r)

    @patch.object(RequestMembershipListViewlet, 'requestCount', new_callable=PropertyMock)
    @patch('gs.group.member.request.adminlist.GroupAdminViewlet.show', new_callable=PropertyMock)
    def test_show_requests(self, m_GAV_s, m_rC):
        'Test that we are shown if we have a request'
        m_GAV_s.return_value = True
        m_rC.return_value = 1
        v = RequestMembershipListViewlet(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        r = v.show

        self.assertTrue(r)

    @patch.object(RequestMembershipListViewlet, 'requestCount', new_callable=PropertyMock)
    @patch('gs.group.member.request.adminlist.GroupAdminViewlet.show', new_callable=PropertyMock)
    def test_show_quiet(self, m_GAV_s, m_rC):
        'Test that we are hidden if we lack a request'
        m_GAV_s.return_value = True
        m_rC.return_value = 0
        v = RequestMembershipListViewlet(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        r = v.show

        self.assertFalse(r)
