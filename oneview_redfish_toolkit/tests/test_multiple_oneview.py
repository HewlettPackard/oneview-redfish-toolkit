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
import json
import unittest

from unittest import mock
from unittest.mock import call

from hpOneView.exceptions import HPOneViewException

from oneview_redfish_toolkit import authentication
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import handler_multiple_oneview
from oneview_redfish_toolkit import multiple_oneview


class TestMultipleOneView(unittest.TestCase):
    """Test class for multiple_oneview"""

    @classmethod
    def setUpClass(self):
        super(TestMultipleOneView, self).setUpClass()

        # Loading server_profile mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        self.sp_uuid = self.server_profile['uri'].split('/')[-1]

        self.not_found_server_profile = HPOneViewException({
            'errorCode': 'ProfileNotFoundException',
            'message': 'The requested profile cannot be retrieved',
        })

        # Creating mocked redfish->Oneview tokens
        self.redfish_token = "redfish_tk1"
        self.ov_tokens = collections.OrderedDict()
        self.ov_tokens["10.0.0.1"] = "ov_tk1"
        self.ov_tokens["10.0.0.2"] = "ov_tk2"
        self.ov_tokens["10.0.0.3"] = "ov_tk3"

    @mock.patch.object(authentication, 'request')
    @mock.patch.object(connection, 'OneViewClient')
    @mock.patch.object(connection, 'get_oneview_client')
    def test_search_in_all_ov_found_on_second(self, get_oneview_client,
                                              oneview_client_mockup,
                                              request):
        # Initializing caches
        multiple_oneview.init_map_resources()
        authentication.init_map_tokens()

        # Mocking redfish->Oneview tokens
        authentication._set_new_token(self.redfish_token, self.ov_tokens)

        # Mocking redfish token on request property
        request.headers.get.return_value = self.redfish_token

        # Mocking OneView client call returning resource for the second
        # one, ip: 10.0.0.2
        oneview_client_mockup.server_profiles.get.side_effect = [
            self.not_found_server_profile,
            self.server_profile,
        ]

        # Mocking connection.get_oneview_client() to return mocked
        # OneView Client
        get_oneview_client.return_value = oneview_client_mockup

        # Create new handler for multiple OneView support
        handler_multiple_ov = \
            handler_multiple_oneview.MultipleOneViewResource()

        # Query resource
        handler_multiple_ov.server_profiles.get(self.sp_uuid)

        # Check if resource was queried on two of three OneViews
        oneview_client_mockup.server_profiles.get.assert_has_calls(
            [call(self.sp_uuid),
             call(self.sp_uuid)]
        )

        # Check if resource was queried on first and the second OneViews
        get_oneview_client.assert_has_calls(
            [call("10.0.0.1", token="ov_tk1"),
             call("10.0.0.2", token="ov_tk2")]
        )

    @mock.patch.object(authentication, 'request')
    @mock.patch.object(connection, 'OneViewClient')
    @mock.patch.object(connection, 'get_oneview_client')
    def test_search_mapped_after_search_in_all(self, get_oneview_client,
                                               oneview_client_mockup,
                                               request):
        # Initializing caches
        multiple_oneview.init_map_resources()
        authentication.init_map_tokens()

        # Mocking redfish->Oneview tokens
        authentication._set_new_token(self.redfish_token, self.ov_tokens)

        # Mocking redfish token on request property
        request.headers.get.return_value = self.redfish_token

        # Mocking OneView client call returning resource just for the last
        # one, ip: 10.0.0.3
        oneview_client_mockup.server_profiles.get.side_effect = [
            self.not_found_server_profile,
            self.not_found_server_profile,
            self.server_profile,
        ]

        # Mocking connection.get_oneview_client() to return mocked
        # OneView Client
        get_oneview_client.return_value = oneview_client_mockup

        # Create new handler for multiple OneView support
        handler_multiple_ov = \
            handler_multiple_oneview.MultipleOneViewResource()

        # Query resource
        handler_multiple_ov.server_profiles.get(self.sp_uuid)

        # Check if resource was queried for all OneViews before found on
        # last one
        oneview_client_mockup.server_profiles.get.assert_has_calls(
            [call(self.sp_uuid),
             call(self.sp_uuid),
             call(self.sp_uuid)]
        )

        # Check if resource was queried on each one for all OneViews
        get_oneview_client.assert_has_calls(
            [call("10.0.0.1", token="ov_tk1"),
             call("10.0.0.2", token="ov_tk2"),
             call("10.0.0.3", token="ov_tk3")]
        )

        # Mocking OneView client call returning resource
        oneview_client_mockup.server_profiles.get.side_effect = [
            self.server_profile,
        ]

        # Query resource again, now already mapped on cache
        handler_multiple_ov.server_profiles.get(self.sp_uuid)

        # Check if resource was queried on just one OneView, the mapped one
        # for the resource
        oneview_client_mockup.server_profiles.get.assert_has_calls(
            [call(self.sp_uuid)]
        )

        # Check if resource was queried on just one OneViews that was mapped
        # for the resource
        get_oneview_client.assert_has_calls(
            [call("10.0.0.3", token="ov_tk3")]
        )

        # Get the OneView IP mapped for the resource
        mapped_ov_ip = multiple_oneview.get_ov_ip_by_resource(self.sp_uuid)

        # Check OneView IP matchs the mapped one
        self.assertEqual(mapped_ov_ip, "10.0.0.3")
