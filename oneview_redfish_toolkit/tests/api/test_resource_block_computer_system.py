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

from oneview_redfish_toolkit.api.resource_block_computer_system \
    import ResourceBlockComputerSystem
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestResourceBlockComputerSystem(BaseTest):
    """Tests for ResourceBlockComputerSystem class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ResourceBlockComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ResourceBlockComputerSystem.json'
        ) as f:
            self.computer_system_mockup = json.load(f)

        # Loading ServerHardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        self.manager_uuid = "b08eb206-a904-46cf-9172-dcdff2fa9639"

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        try:
            computer_system = ResourceBlockComputerSystem(
                self.server_hardware, self.manager_uuid
            )
        except Exception as e:
            self.fail(
                "Failed to instantiate ResourceBlockComputerSystem class."
                " Error: {}".format(e))

        self.assertIsInstance(computer_system, ResourceBlockComputerSystem)

    def test_serialize(self):
        # Tests the serialize function result against known result
        try:
            computer_system = ResourceBlockComputerSystem(
                self.server_hardware, self.manager_uuid
            )
        except Exception as e:
            self.fail(
                "Failed to instantiate ResourceBlockComputerSystem class."
                " Error: {}".format(e))
        try:
            result = json.loads(computer_system.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqualMockup(self.computer_system_mockup, result)
