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

from oneview_redfish_toolkit.api.resource_block_ethernet_interface \
    import ResourceBlockEthernetInterface
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestResourceBlockEthernetInterface(BaseTest):
    """Tests for ResourceBlockEthernetInterface class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ResourceBlockEthernetInterface mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ResourceBlockEthernetInterface.json'
        ) as f:
            self.ethernet_interface_mockup = json.load(f)

        # Loading ServerProfileTemplate connection mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplate.json'
        ) as f:
            self.spt_mockup = json.load(f)

        # Loading EthernetNetowrk mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/EthernetNetwork.json'
        ) as f:
            self.ethernet_network_mockup = json.load(f)

        connection_settings = self.spt_mockup["connectionSettings"]

        self.connection_mockup = connection_settings["connections"][0]

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        ethernet_interface = ResourceBlockEthernetInterface(
            self.spt_mockup,
            self.connection_mockup,
            self.ethernet_network_mockup)

        self.assertIsInstance(
            ethernet_interface, ResourceBlockEthernetInterface)

    def test_serialize(self):
        # Tests the serialize function result against known result
        ethernet_interface = ResourceBlockEthernetInterface(
            self.spt_mockup,
            self.connection_mockup,
            self.ethernet_network_mockup)

        result = json.loads(ethernet_interface.serialize())

        self.assertEqualMockup(self.ethernet_interface_mockup, result)
