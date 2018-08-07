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
from oneview_redfish_toolkit.blueprints import network_port
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestNetworkPort(BaseFlaskTest):
    """Tests for NetworkPort blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestNetworkPort, self).setUpClass()

        self.app.register_blueprint(network_port.network_port)

    def test_get_network_port(self):
        """Tests NetworkPort"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading NetworkPort mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkPort1-Ethernet.json'
        ) as f:
            network_port_mockup = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = server_hardware

        # Get NetworkPort
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/3/NetworkPorts/1"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_port_mockup, result)

    def test_get_network_port_fibre_channel(self):
        """Tests NetworkPort"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardwareFibreChannel.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading NetworkPort mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkPort1-FibreChannel.json'
        ) as f:
            network_port_mockup = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = server_hardware

        # Get NetworkPort
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/2/NetworkPorts/1"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_port_mockup, result)

    def test_get_network_port_invalid_device_id(
        self):
        """Tests NetworkPort"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = server_hardware

        # Get NetworkPort
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/invalid_id/NetworkPorts/1"
        )

        # Tests response
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_port_sh_not_found(self):
        """Tests NetworkPort server hardware not found"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkPort
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/3/NetworkPorts/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_port_sh_exception(self):
        """Tests NetworkPort unknown exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkPort
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/3/NetworkPorts/1"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
