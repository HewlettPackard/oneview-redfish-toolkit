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

# Python libs
import json

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import network_adapter
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestNetworkAdapter(BaseFlaskTest):
    """Tests for NetworkAdapter blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestNetworkAdapter, self).setUpClass()

        self.app.register_blueprint(network_adapter.network_adapter)

    def test_get_network_interface(self):
        """Tests NetworkAdapter"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading NetworkAdapter mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkAdapters3.json'
        ) as f:
            network_adapter_mockup = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = server_hardware

        # Get NetworkAdapter
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/3"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_adapter_mockup, result)

    def test_get_network_interface_invalid_id(self):
        """Tests NetworkAdapter"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = server_hardware

        # Get NetworkAdapter
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/invalid_id"
        )

        # Tests response
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_interface_sh_not_found(self):
        """Tests NetworkAdapter server hardware not found"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkAdapter
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/3"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_interface_sh_exception(
        self):
        """Tests NetworkAdapter unknown exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkAdapter
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/3"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
