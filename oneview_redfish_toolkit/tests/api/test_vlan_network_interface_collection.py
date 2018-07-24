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

import json

from oneview_redfish_toolkit.api.vlan_network_interface_collection \
    import VLanNetworkInterfaceCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestVLanNetworkInterfaceCollection(BaseTest):
    """Tests for VLanNetworkInterfaceCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading NetworkSet mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/NetworkSet.json'
        ) as f:
            self.network_set_mockup = json.load(f)

        # Loading VLanNetworkInterfaceCollection mockup value
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/VLanNetworkInterfaceCollectionSPT.json'
        ) as f:
            self.vlan_network_interface_collection = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        vlan_network_interface_collection = VLanNetworkInterfaceCollection(
            self.network_set_mockup,
            self.vlan_network_interface_collection["@odata.id"])

        self.assertIsInstance(
            vlan_network_interface_collection, VLanNetworkInterfaceCollection)

    def test_serialize(self):
        # Tests the serialize function result against known result
        vlan_network_interface_collection = VLanNetworkInterfaceCollection(
            self.network_set_mockup,
            self.vlan_network_interface_collection["@odata.id"])

        result = json.loads(vlan_network_interface_collection.serialize())

        self.assertEqualMockup(self.vlan_network_interface_collection, result)
