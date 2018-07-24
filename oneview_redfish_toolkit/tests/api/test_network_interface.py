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

import json

from oneview_redfish_toolkit.api.network_interface import \
    NetworkInterface
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestNetworkInterface(BaseTest):
    """Tests for NetworkInterface class"""

    def setUp(self):
        """Tests preparation"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/NetworkInterface3.json'
        ) as f:
            self.network_interface_mockup = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        device_id = "3"

        network_interface = \
            NetworkInterface(device_id,
                             self.server_profile,
                             self.server_hardware)

        result = json.loads(network_interface.serialize())

        self.assertEqualMockup(self.network_interface_mockup, result)
