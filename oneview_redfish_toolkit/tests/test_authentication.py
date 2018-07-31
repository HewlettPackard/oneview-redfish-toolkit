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

from oneview_redfish_toolkit import authentication
from oneview_redfish_toolkit import config


class TestAuthentication(unittest.TestCase):
    """Test class for authentication"""

    @mock.patch.object(authentication, 'OneViewClient')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    def test_map_token_redfish_for_multiple_ov(self, get_oneview_multiple_ips,
                                               oneview_client_mockup):
        tokens_ov = collections.OrderedDict({'10.0.0.1': 'abc',
                                             '10.0.0.2': 'def',
                                             '10.0.0.3': 'ghi'})
        list_ips = list(tokens_ov.keys())
        list_tokens = list(tokens_ov.values())
        iter_tokens_ov = iter(list_tokens)

        get_oneview_multiple_ips.return_value = list_ips

        def function_returning_token():
            return next(iter_tokens_ov)

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.side_effect = \
            function_returning_token

        # Check if redfish token return is one of the OneView's token
        rf_token = authentication.login('user', 'password')
        self.assertTrue(rf_token in list_tokens)

        # Check if cached token map has the Redfish token return on login
        map_tokens = authentication._get_map_tokens()
        self.assertTrue(rf_token in map_tokens)

        # Check if cached token map has the correct OneViewIp/OneViewToken
        # tuples
        for ov_ip, ov_token in map_tokens[rf_token].items():
            self.assertEqual(tokens_ov[ov_ip], ov_token)
