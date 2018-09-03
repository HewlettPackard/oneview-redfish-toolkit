# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
    Tests for store_schema and load_registry function from util.py
"""
import collections
import unittest

from unittest import mock

from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config


class TestAuthentication(unittest.TestCase):
    """Test class for authentication"""

    @mock.patch('oneview_redfish_toolkit.connection.OneViewClient')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    @mock.patch.object(config, 'auth_mode_is_conf')
    @mock.patch.object(config, 'auth_mode_is_session')
    def test_map_token_redfish_for_multiple_ov(self, conf_auth_mode,
                                               session_auth_mode,
                                               get_oneview_multiple_ips,
                                               oneview_client_mockup):
        conf_auth_mode.return_value = True
        session_auth_mode.return_value = False
        mocked_rf_token = "abc"
        conn_1 = mock.MagicMock()

        unsorted_conns_ov = {'10.0.0.1': conn_1,
                             '10.0.0.2': mock.MagicMock(),
                             '10.0.0.3': mock.MagicMock()}
        connections_ov = collections.OrderedDict(
            sorted(unsorted_conns_ov.items(), key=lambda t: t[0]))
        list_ips = list(connections_ov.keys())
        iter_conns_ov = iter(list(connections_ov.values()))

        client_session.init_map_clients()

        get_oneview_multiple_ips.return_value = list_ips

        def function_returning_token(ov_config):
            return next(iter_conns_ov)

        oneview_client_mockup.side_effect = function_returning_token
        conn_1.connection.get_session_id.return_value = mocked_rf_token

        # Check if redfish token return is one of the OneView's token
        rf_token = client_session.login('user', 'password')
        oneview_client_mockup.assert_any_call(
            {
                'ip': '10.0.0.1',
                'credentials': {'userName': 'user', 'password': 'password'},
                'api_version': 600
            }
        )
        self.assertEqual(rf_token, mocked_rf_token)

        # Check if cached connection map has the Redfish token return on login
        map_clients = client_session._get_map_clients()
        self.assertTrue(rf_token in map_clients)

        # Check if cached connection map has the correct
        # OneViewIp/OneViewConnection tuples
        for ov_ip, ov_conn in map_clients[rf_token].items():
            self.assertEqual(connections_ov[ov_ip], ov_conn)

    @mock.patch.object(authentication, 'OneViewClient')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    def test_login_with_specific_login_domain_for_multiple_ov(
            self, get_oneview_multiple_ips, oneview_client_mockup):

        tokens_ov = collections.OrderedDict({'10.0.0.1': 'abc',
                                             '10.0.0.2': 'def',
                                             '10.0.0.3': 'ghi'})
        list_ips = list(tokens_ov.keys())

        authentication.init_map_tokens()

        get_oneview_multiple_ips.return_value = list_ips

        authentication.login('SOME_DOMAIN\\user', 'password123')

        oneview_client_mockup.assert_any_call(
            {
                'ip': '10.0.0.1',
                'credentials': {
                    'userName': 'user',
                    'password': 'password123',
                    'authLoginDomain': 'SOME_DOMAIN'
                },
                'api_version': 600
            }
        )

    def test_create_credentials(self):
        # when username and password are simple values
        result = authentication.create_credentials('administrator', 'pwd123')
        self.assertEqual(result, {
            'userName': 'administrator',
            'password': 'pwd123'
        })

        # when username has auth login domain
        result = authentication.create_credentials('LOCAL\\administrator',
                                                   'pwd123')
        self.assertEqual(result, {
            'userName': 'administrator',
            'password': 'pwd123',
            'authLoginDomain': 'LOCAL'
        })

        # when username and password are empty values
        result = authentication.create_credentials('', '')
        self.assertEqual(result, {
            'userName': '',
            'password': ''
        })

        # when username and password are None
        result = authentication.create_credentials(None, None)
        self.assertEqual(result, {
            'userName': None,
            'password': None
        })
