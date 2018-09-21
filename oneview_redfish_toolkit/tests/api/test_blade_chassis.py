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
import copy
import json

from oneview_redfish_toolkit.api.blade_chassis import BladeChassis
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestBladeChassis(BaseTest):
    """Tests for Chassis class"""

    def setUp(self):
        """Tests preparation"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading Chassis mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/BladeChassis.json'
        ) as f:
            self.blade_chassis_mockup = json.load(f)

        self.manager_uuid = "b08eb206-a904-46cf-9172-dcdff2fa9639"

    def test_serialize_when_blade_chassis_has_computer_system(self):
        blade_chassis = BladeChassis(
            self.server_hardware, self.manager_uuid
        )

        result = json.loads(blade_chassis.serialize())

        self.assertEqualMockup(self.blade_chassis_mockup, result)

    def test_serialize_when_blade_chassis_has_not_computer_system(self):
        server_hardware = copy.deepcopy(self.server_hardware)
        server_hardware["serverProfileUri"] = None

        blade_chassis = BladeChassis(
            server_hardware, self.manager_uuid
        )
        result = json.loads(blade_chassis.serialize())

        expected_blade_result = copy.deepcopy(self.blade_chassis_mockup)
        expected_blade_result["Links"]["ComputerSystems"] = []

        self.assertEqualMockup(expected_blade_result, result)

        server_hardware["serverProfileUri"] = ""

        blade_chassis = BladeChassis(
            server_hardware, self.manager_uuid
        )
        result = json.loads(blade_chassis.serialize())

        self.assertEqualMockup(expected_blade_result, result)
