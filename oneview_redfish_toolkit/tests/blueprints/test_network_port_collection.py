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
from unittest import mock

# Module libs
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit.blueprints import network_port_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestNetworkPortCollection(BaseFlaskTest):
    """Tests for NetworkPortCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestNetworkPortCollection, self).setUpClass()

        self.app.register_blueprint(
            network_port_collection.network_port_collection)

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

    def test_get_network_port_collection(self):
        """Tests NetworkInterfaceCollection"""

        # Loading NetworkPortCollection mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkPortCollection.json'
        ) as f:
            network_port_collection_mockup = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        # Get NetworkPortCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/1/NetworkPorts/"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_port_collection_mockup, result)

    @mock.patch.object(RedfishJsonValidator, "get_resource_by_id")
    def test_get_network_port_collection_empty(self, get_resource_by_id):
        """Tests NetworkPortCollection empty server hardware"""

        # Loading NetworkPortCollectionEmpty mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'NetworkPortCollectionEmpty.json'
        ) as f:
            network_port_collection_empty = json.load(f)

        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        # Get NetworkPortCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/1/NetworkPorts/"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_port_collection_empty, result)

    def test_get_network_port_collection_sh_exception(self):
        """Tests NetworkPortCollection with exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkPortCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/1/NetworkPorts/"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_port_collection_invalid_device_id(self):
        """Tests NetworkPortCollection with invalid device id"""

        self.oneview_client.server_hardware.get.side_effect = \
            Exception("Invalid id for device")

        # Get invalid NetworkPortCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/100/NetworkPorts/"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
