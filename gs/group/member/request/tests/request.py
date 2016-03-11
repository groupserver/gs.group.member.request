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
from gs.group.member.request.request import (RequestForm, )


class TestRequestForm(TestCase):
    '''Test the ``RequestMembershipListViewlet`` class'''

    @patch.object(RequestForm, 'userInfo', new_callable=PropertyMock)
    @patch.object(RequestForm, 'groupInfo', new_callable=PropertyMock)
    @patch.object(RequestForm, 'siteInfo', new_callable=PropertyMock)
    @patch('gs.group.member.request.request.MessageSender.send_message')
    @patch('gs.group.member.request.request.getMultiAdapter')
    @patch('gs.group.member.request.request.log.warn')
    def test_send_message_no_verified(self, m_log_warn, m_gMA, m_MS_s_m, m_sI, m_gI, m_uI):
        'Test that an admin can lack a verified email address'
        m_uI().id = 'durk'
        m_uI().name = 'Durk'
        m_gI().id = 'example_group'
        m_gI().name = 'Example group'
        m_sI().id = 'example'
        m_sI().name = 'Example site'
        m_MS_s_m.side_effect = ValueError('Bung')
        m_gMA.side_effect = [lambda: 'Text', lambda: '<p>HTML</p>', ]

        context = MagicMock()
        request = MagicMock()
        rf = RequestForm(context, request)

        adminInfo = MagicMock()
        adminInfo.id = 'dinsdale'
        adminInfo.name = 'Dinsdale'
        rf.send_message('example@groups.example.com', adminInfo,
                        'You have broke the unwritten rule.')

        self.assertEqual(1, m_log_warn.call_count)

    @patch.object(RequestForm, 'userInfo', new_callable=PropertyMock)
    @patch.object(RequestForm, 'groupInfo', new_callable=PropertyMock)
    @patch.object(RequestForm, 'siteInfo', new_callable=PropertyMock)
    @patch('gs.group.member.request.request.MessageSender.send_message')
    @patch('gs.group.member.request.request.getMultiAdapter')
    @patch('gs.group.member.request.request.log.warn')
    def test_send_message(self, m_log_warn, m_gMA, m_MS_s_m, m_sI, m_gI, m_uI):
        'Test that we can send the verification message'
        m_uI().id = 'durk'
        m_uI().name = 'Durk'
        m_gI().id = 'example_group'
        m_gI().name = 'Example group'
        m_sI().id = 'example'
        m_sI().name = 'Example site'
        m_gMA.side_effect = [lambda: 'Text', lambda: '<p>HTML</p>', ]

        context = MagicMock()
        request = MagicMock()
        rf = RequestForm(context, request)

        adminInfo = MagicMock()
        adminInfo.id = 'dinsdale'
        adminInfo.name = 'Dinsdale'
        rf.send_message('example@groups.example.com', adminInfo,
                        'You have broke the unwritten rule.')

        self.assertEqual(0, m_log_warn.call_count)
        m_MS_s_m.assert_called_once_with('request-admin-message-subject', 'Text', '<p>HTML</p>',
                                         'example@groups.example.com')
