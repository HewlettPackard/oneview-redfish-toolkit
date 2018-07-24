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

from oneview_redfish_toolkit.api.ethernet_interface import \
    EthernetInterface
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestEthernetInterface(BaseTest):
    """Tests for EthernetInterface class"""

    def setUp(self):
        """Tests preparation"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

    def test_serialize_when_it_has_only_one_vlan(self):
        # Tests the serialize function result against known result for
        # a ethernet interface with only one vlan

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'NetworkForEthernetInterface.json'
        ) as f:
            network = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EthernetInterfaceWithOnlyOneVlan.json'
        ) as f:
            ethernet_interface_mockup = json.load(f)

        conn_id_1 = self.server_profile["connectionSettings"]["connections"][0]

        ethernet_interface = \
            EthernetInterface(self.server_profile,
                              conn_id_1,
                              network)

        result = json.loads(ethernet_interface.serialize())

        self.assertEqualMockup(ethernet_interface_mockup, result)

    def test_serialize_when_it_has_a_list_of_vlans(self):
        # Tests the serialize function result against known result for
        # a ethernet interface with list of vlans

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'NetworkSetForEthernetInterface.json'
        ) as f:
            network_set = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EthernetInterfaceWithListOfVlans.json'
        ) as f:
            ethernet_interface_mockup = json.load(f)

        conn_id_2 = self.server_profile["connectionSettings"]["connections"][1]

        ethernet_interface = \
            EthernetInterface(self.server_profile,
                              conn_id_2,
                              network_set)

        result = json.loads(ethernet_interface.serialize())

        self.assertEqualMockup(ethernet_interface_mockup, result)
