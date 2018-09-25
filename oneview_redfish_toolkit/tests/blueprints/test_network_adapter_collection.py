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
import copy
import json

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import network_adapter_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestNetworkAdapterCollection(BaseFlaskTest):
    """Tests for NetworkAdapterCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestNetworkAdapterCollection, self).setUpClass()

        self.app.register_blueprint(
            network_adapter_collection.network_adapter_collection)

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

    def test_get_network_adapter_collection(self):
        """Tests NetworkAdapterCollection"""

        # Loading NetworkAdapterCollection mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkAdapterCollection.json'
        ) as f:
            network_adapter_collection_mockup = json.load(f)

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        # Get NetworkAdapterCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_adapter_collection_mockup, result)

    def test_get_network_adapter_collection_sh_not_found(self):
        """Tests NetworkAdapterCollection"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkAdapterCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_adapter_collection_sh_exception(self):
        """Tests NetworkAdapterCollection"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        self.oneview_client.server_hardware.get.side_effect = e

        # Get NetworkAdapterCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_get_network_collection_empty(self):
        """Tests NetworkAdapterCollection empty list"""

        # Loading NetworkAdapterCollectionEmpty mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'NetworkAdapterCollectionEmpty.json'
        ) as f:
            network_adapter_collection_empty = json.load(f)

        server_hardware = copy.deepcopy(self.server_hardware)
        server_hardware["portMap"]["deviceSlots"] = []

        # Create mock response
        self.oneview_client.server_hardware.get.return_value = \
            server_hardware

        # Get NetworkAdapterCollection
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752/"
            "NetworkAdapters/"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_adapter_collection_empty, result)
