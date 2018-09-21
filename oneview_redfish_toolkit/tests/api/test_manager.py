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

from oneview_redfish_toolkit.api.manager import Manager
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestManager(BaseTest):
    """Tests for Manager class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ApplianceNodeInfo mockup result
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ApplianceNodeInfo.json'
        ) as f:
            self.appliance_node_info = json.load(f)

        # Loading ApplianceState mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceState.json'
        ) as f:
            self.appliance_state = json.load(f)

        # Loading ApplianceHealthStatus mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceHealthStatus.json'
        ) as f:
            self.appliance_health_status = json.load(f)

        # Loading Manager mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'Manager.json'
        ) as f:
            self.manager_mockup = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        computer_system = Manager(
            self.appliance_node_info,
            self.appliance_state,
            self.appliance_health_status
        )

        result = json.loads(computer_system.serialize())

        self.assertEqualMockup(self.manager_mockup, result)
