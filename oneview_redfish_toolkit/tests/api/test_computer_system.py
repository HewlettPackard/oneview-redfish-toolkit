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

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
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

        # Loading ServerProfile mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        # Loading Drives mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Drives.json'
        ) as f:
            self.drives = json.load(f)

        # Loading LabelForServerProfile mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview'
                '/LabelForServerProfile.json'
        ) as f:
            self.label_for_server_profile = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/ComputerSystem.json'
        ) as f:
            self.computer_system_mockup = json.load(f)

        self.manager_uuid = "b08eb206-a904-46cf-9172-dcdff2fa9639"

    def test_serialize(self):
        # Tests the serialize function result against known result
        spt_uuid = "61c3a463-1355-4c68-a4e3-4f08c322af1b"
        computer_system = ComputerSystem(
            self.server_hardware,
            self.server_hardware_types,
            self.server_profile,
            [self.drives[4]],
            spt_uuid,
            self.manager_uuid
        )

        result = json.loads(computer_system.serialize())

        self.assertEqualMockup(self.computer_system_mockup, result)
