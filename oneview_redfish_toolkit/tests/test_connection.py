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

from oneview_redfish_toolkit import connection
import unittest
from unittest import mock


class TestUtil(unittest.TestCase):
    """Test class for util

        Tests:
            get_oneview_client()
                - connection recover
                - connection renew
                - connection failure
    """

    # load_conf() tests
    def setUp(self):
        self.schema_dir = './oneview_redfish_toolkit/schemas'
        self.registry_dir = './oneview_redfish_toolkit/registry'
        self.config_file = './oneview_redfish_toolkit/conf/redfish.conf'

    @mock.patch.object(connection, 'OneViewClient')
    def test_get_ov_client_recover(self, oneview_client_mockup):
        # Tests a successful recover of a OV client

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get.return_value = list()

        try:
            ov_client = connection.OneViewClient({})
        except Exception as e:
            self.fail('Failed to connect to OneView: '.format(e))
        self.assertIsNotNone(ov_client)

    @mock.patch.object(connection, 'OneViewClient')
    def test_get_ov_client_renew(self, oneview_client_mockup):
        """Tests getting a OV client from expired session"""

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get.return_value = \
            Exception('session expired')
        oneview_client.connection.login.return_value = oneview_client

        try:
            ov_client = connection.OneViewClient({})
        except Exception as e:
            self.fail('Failed to connect to OneView: '.format(e))
        self.assertIsNotNone(ov_client)

    @mock.patch.object(connection, 'OneViewClient')
    def test_get_ov_client_oneview_offline(self, oneview_client_mockup):
        """Tests getting a OV client from an offline oneview"""

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get.return_value = \
            Exception('OneView not responding')
        oneview_client.connection.login.return_value = \
            Exception('OneView not responding')

        try:
            ov_client = connection.OneViewClient({})
        except Exception as e:
            self.fail('Failed to connect to OneView: '.format(e))
        self.assertIsNotNone(ov_client)
