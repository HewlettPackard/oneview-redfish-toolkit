# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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
from jsonschema.exceptions import ValidationError

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestComputerSystem(BaseTest):
    """Tests for ComputerSystem class"""

    def setUp(self):
        """Tests preparation"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwareTypes.json'
        ) as f:
            self.server_hardware_types = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/ComputerSystem.json'
        ) as f:
            self.computer_system_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            computer_system = ComputerSystem(
                self.server_hardware,
                self.server_hardware_types
            )
        except Exception as e:
            self.fail("Failed to instantiate ComputerSystem class."
                      " Error: {}".format(e))
        self.assertIsInstance(computer_system, ComputerSystem)

    def test_failing_class_instantiation(self):
        # Tests if validation fail
        # The name must be a string
        self.server_hardware["name"] = 1

        with self.assertRaises(ValidationError):
            ComputerSystem(self.server_hardware, self.server_hardware_types)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            computer_system = ComputerSystem(
                self.server_hardware,
                self.server_hardware_types
            )
        except Exception as e:
            self.fail("Failed to instantiate ComputerSystem class."
                      " Error: {}".format(e))

        try:
            result = json.loads(computer_system.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.computer_system_mockup, result)

    def test_get_oneview_power_configuration(self):
        # Tests invalid mapping values of power state
        #
        obj = ComputerSystem(self.server_hardware, self.server_hardware_types)

        self.assertRaises(OneViewRedfishError, obj.
                          get_oneview_power_configuration, "ForceOn")

        self.assertRaises(OneViewRedfishError, obj.
                          get_oneview_power_configuration, "INVALID")
