# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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

import json
import os
import socket

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.event import Event
from oneview_redfish_toolkit.api.subscription import Subscription
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import util
import unittest
from unittest import mock


class TestUtil(unittest.TestCase):
    """Test class for util

        Tests:
            load_conf()
                - invalid ini file
                - valid ini file
                - have all expected sessions
                - have all expected options
                - checks if globals vars are not none

    """

    # load_conf() tests
    def setUp(self):
        self.schema_dir = './oneview_redfish_toolkit/schemas'
        self.registry_dir = './oneview_redfish_toolkit/registry'
        self.config_file = './oneview_redfish_toolkit/conf/redfish.conf'

    def test_get_ip(self):
        # Tests get_ip function; This test may not work if it returns an IPV6.
        ip = util.get_ip()
        try:
            socket.inet_aton(ip)
        except Exception:
            self.fail("Failed to get a valid IP Address")

    @mock.patch.object(connection, 'check_oneview_availability')
    def test_create_certs(
        self, check_ov_availability):
        # Test generate_certificate function

        config.load_config(self.config_file)

        util.generate_certificate("oneview_redfish_toolkit/",
                                  "test", 2048)

        self.assertTrue(os.path.exists(os.path.join("oneview_redfish_toolkit",
                        "test" + ".crt")))
        self.assertTrue(os.path.exists(os.path.join("oneview_redfish_toolkit",
                        "test" + ".key")))

    @mock.patch.object(connection, 'check_oneview_availability')
    def test_load_event_service_invalid_info(
        self, check_ov_availability):
        self.assertRaises(
            OneViewRedfishError, config.load_config(self.config_file))

    @mock.patch.object(connection, 'check_oneview_availability')
    @mock.patch.object(util, 'subscriptions_by_type')
    @mock.patch(
        'oneview_redfish_toolkit.event_dispatcher.EventDispatcher.start')
    def test_submit_event_with_subscriber(
        self, start_mock, subscription_mock, check_ov_availability):
        """Tests SubmitTestEvent action with two subscribers"""

        config.load_config(self.config_file)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            event_mockup = Event(json.loads(f.read()))

        subscription_mock['Alert'].values.return_value = [
            Subscription('1', 'destination1', [], 'context1'),
            Subscription('2', 'destination2', [], 'context2')
        ]

        util.dispatch_event(event_mockup)

        self.assertTrue(start_mock.call_count == 2)

    @mock.patch.object(connection, 'check_oneview_availability')
    @mock.patch.object(util, 'subscriptions_by_type')
    @mock.patch(
        'oneview_redfish_toolkit.event_dispatcher.EventDispatcher.start')
    def test_submit_event_without_subscriber(
        self, start_mock, subscription_mock, check_ov_availability):
        """Tests SubmitTestEvent action with no subscribers"""

        config.load_config(self.config_file)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            event_mockup = Event(json.loads(f.read()))

        subscription_mock['Alert'].values.return_value = []

        util.dispatch_event(event_mockup)

        self.assertFalse(start_mock.called)
