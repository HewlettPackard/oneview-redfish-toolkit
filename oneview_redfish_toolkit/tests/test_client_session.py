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
from collections import OrderedDict
import unittest
from unittest import mock
from unittest.mock import call

from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import multiple_oneview


class TestAuthentication(unittest.TestCase):
    """Test class for authentication"""

    def setUp(self):
        client_session.init_map_clients()
        multiple_oneview.init_map_appliances()

    @mock.patch.object(client_session, 'uuid')
    @mock.patch('oneview_redfish_toolkit.connection.OneViewClient')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    @mock.patch.object(config, 'get_authentication_mode')
    def test_map_token_redfish_for_multiple_ov(self, get_authentication_mode,
                                               get_oneview_multiple_ips,
                                               oneview_client_mockup,
                                               uuid_mock):
        get_authentication_mode.return_value = 'session'
        mocked_rf_token = "abc"
        session_id = '123456'
        list_ips = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
        conn_1 = mock.MagicMock()

        connection_list = [conn_1, mock.MagicMock(), mock.MagicMock()]

        connections_ov = collections.OrderedDict({
            'client_ov_by_ip': {
                list_ips[0]: connection_list[0],
                list_ips[1]: connection_list[1],
                list_ips[2]: connection_list[2]
            },
            'session_id': session_id
        })

        uuid_mock.uuid4.return_value = session_id

        iter_conns_ov = iter(connection_list)

        client_session.init_map_clients()

        get_oneview_multiple_ips.return_value = list_ips

        def function_returning_token(ov_config):
            return next(iter_conns_ov)

        oneview_client_mockup.side_effect = function_returning_token
        conn_1.connection.get_session_id.return_value = mocked_rf_token

        # Check if redfish token return is one of the OneView's token
        rf_token, _ = client_session.login('user', 'password')
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

    @mock.patch.object(connection, 'OneViewClient')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    @mock.patch.object(config, 'get_authentication_mode')
    def test_login_with_specific_login_domain_for_multiple_ov(
            self, get_authentication_mode,
            get_oneview_multiple_ips, oneview_client_mockup):

        get_authentication_mode.return_value = 'session'
        tokens_ov = collections.OrderedDict({'10.0.0.1': 'abc',
                                             '10.0.0.2': 'def',
                                             '10.0.0.3': 'ghi'})
        list_ips = list(tokens_ov.keys())

        client_session.init_map_clients()

        get_oneview_multiple_ips.return_value = list_ips

        client_session.login('SOME_DOMAIN\\user', 'password123')

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
        result = connection.create_credentials('administrator', 'pwd123')
        self.assertEqual(result, {
            'userName': 'administrator',
            'password': 'pwd123'
        })

        # when username has auth login domain
        result = connection.create_credentials('LOCAL\\administrator',
                                               'pwd123')
        self.assertEqual(result, {
            'userName': 'administrator',
            'password': 'pwd123',
            'authLoginDomain': 'LOCAL'
        })

        # when username and password are empty values
        result = connection.create_credentials('', '')
        self.assertEqual(result, {
            'userName': '',
            'password': ''
        })

        # when username and password are None
        result = connection.create_credentials(None, None)
        self.assertEqual(result, {
            'userName': None,
            'password': None
        })

    @mock.patch.object(client_session, 'uuid')
    @mock.patch.object(client_session, 'time')
    @mock.patch.object(client_session, 'threading')
    def test_garbage_collector_for_expired_sessions(self,
                                                    threading_mock,
                                                    time_mock,
                                                    uuid_mock):
        thread_obj_mock = mock.Mock()
        threading_mock.Thread.return_value = thread_obj_mock

        # using time.sleep to exit from loop raising an InterruptedError
        time_mock.sleep.side_effect = [None, InterruptedError]

        # Client 1 will represents the success request, must be in the cache
        # Client 2 will represents the fail request, must be removed from
        # the cache

        client_1 = mock.Mock()
        client_2 = mock.Mock()
        resp_1 = mock.Mock(status=200)
        resp_2 = mock.Mock(status=404)
        uuid_mock.uuid4.side_effect = ['session_id_1', 'session_id_2']

        client_1.connection.get_session_id.return_value = 'ov_session_abc'
        client_2.connection.get_session_id.return_value = 'ov_session_def'

        client_1.connection.do_http.return_value = (resp_1, None)
        client_2.connection.do_http.return_value = (resp_2, None)

        client_session._set_new_client_by_token('abc', {'10.0.0.11': client_1})
        client_session._set_new_client_by_token('def', {'10.0.0.12': client_2})

        expected_map_client = OrderedDict()
        expected_map_client['abc'] = {
            'client_ov_by_ip': {'10.0.0.11': client_1},
            'session_id': 'session_id_1'
        }

        client_session.init_gc_for_expired_sessions()
        try:
            client_session._gc_for_expired_sessions()
        except InterruptedError:
            pass

        self.assertEqual(expected_map_client,
                         client_session._get_map_clients())

        threading_mock.Thread.assert_called_with(
            target=client_session._gc_for_expired_sessions,
            daemon=True)
        thread_obj_mock.start.assert_called_with()
        time_mock.sleep.assert_called_with(client_session.GC_FREQUENCY_IN_SEC)

        client_1.connection.do_http.assert_called_with('GET',
                                                       '/rest/sessions/',
                                                       '',
                                                       {'Session-Id':
                                                        'ov_session_abc'})
        client_2.connection.do_http.assert_called_with('GET',
                                                       '/rest/sessions/',
                                                       '',
                                                       {'Session-Id':
                                                        'ov_session_def'})

    @mock.patch.object(client_session, 'time')
    def test_garbage_collector_loop(self, time_mock):
        time_mock.sleep.side_effect = [None, None, None, InterruptedError]

        try:
            client_session._gc_for_expired_sessions()
        except InterruptedError:
            pass

        time_mock.sleep.assert_called_with(client_session.GC_FREQUENCY_IN_SEC)
        self.assertEqual(4, time_mock.sleep.call_count)

    @mock.patch.object(client_session, 'uuid')
    @mock.patch.object(client_session, 'logging')
    @mock.patch.object(client_session, 'time')
    def test_garbage_collector_for_expired_sessions_when_raises_exception(
            self, time_mock, logging_mock, uuid_mock):
        time_mock.sleep.side_effect = [None, InterruptedError]

        uuid_mock.uuid4.return_value = 'session_id_1'

        client = mock.Mock()
        client.connection.do_http.side_effect = Exception('Some error message')
        client_session._set_new_client_by_token('abc', {'10.0.0.11': client})

        expected_map_client = OrderedDict()
        expected_map_client['abc'] = {
            'client_ov_by_ip': {'10.0.0.11': client},
            'session_id': 'session_id_1'
        }

        try:
            client_session._gc_for_expired_sessions()
        except InterruptedError:
            pass

        logging_mock.exception.assert_called_with(
            'Unexpected error: Some error message')
        self.assertEqual(expected_map_client,
                         client_session._get_map_clients())

    @mock.patch.object(client_session, 'uuid')
    @mock.patch.object(client_session, 'logging')
    @mock.patch.object(client_session, 'time')
    def test_garbage_collector_when_ov_request_status_is_not_200_neither_404(
            self, time_mock, logging_mock, uuid_mock):
        time_mock.sleep.side_effect = [None, None, None, None,
                                       InterruptedError]

        client = mock.Mock()
        client.connection.do_http.side_effect = [
            (mock.Mock(status=400), 'request body 1'),
            (mock.Mock(status=401), 'request body 2'),
            (mock.Mock(status=403), 'request body 3'),
            (mock.Mock(status=500), 'request body 4')
        ]
        uuid_mock.uuid4.return_value = 'session_id_1'
        client_session._set_new_client_by_token('abc', {'10.0.0.11': client})

        expected_map_client = OrderedDict()
        expected_map_client['abc'] = {
            'client_ov_by_ip': {'10.0.0.11': client},
            'session_id': 'session_id_1'
        }

        try:
            client_session._gc_for_expired_sessions()
        except InterruptedError:
            pass

        logging_mock.error.assert_has_calls([
            call(
                'Unexpected response with status 400 of Oneview sessions '
                'endpoint: request body 1'
            ),
            call(
                'Unexpected response with status 401 of Oneview sessions '
                'endpoint: request body 2'
            ),
            call(
                'Unexpected response with status 403 of Oneview sessions '
                'endpoint: request body 3'
            ),
            call(
                'Unexpected response with status 500 of Oneview sessions '
                'endpoint: request body 4'
            )
        ])
        self.assertEqual(expected_map_client,
                         client_session._get_map_clients())
