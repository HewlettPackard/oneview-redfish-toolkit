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

from oneview_redfish_toolkit.api.ethernet_interface_collection import \
    EthernetInterfaceCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestEthernetInterfaceCollection(BaseTest):
    """Tests for EthernetInterfaceCollection class"""

    def setUp(self):
        """Tests preparation"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EthernetInterfaceCollection.json'
        ) as f:
            self.ethernet_interface_collection_mockup = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        ethernet_interface_collection = \
            EthernetInterfaceCollection(self.server_profile)

        result = json.loads(ethernet_interface_collection.serialize())

        self.assertEqualMockup(self.ethernet_interface_collection_mockup,
                               result)
