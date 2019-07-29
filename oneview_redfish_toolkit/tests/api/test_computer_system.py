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

from copy import deepcopy
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

    def test_build_composed_system(self):
        spt_uuid = "61c3a463-1355-4c68-a4e3-4f08c322af1b"
        computer_system = ComputerSystem.build_composed_system(
            self.server_hardware,
            self.server_hardware_types,
            self.server_profile,
            [self.drives[4]],
            spt_uuid,
            self.manager_uuid,
            []
        )

        result = json.loads(computer_system.serialize())

        self.assertEqualMockup(self.computer_system_mockup, result)

    def test_build_composed_system_with_external_storage(self):
        volume_resource_block = {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/"
            "volume_uuid"
        }
        computer_system_mockup = deepcopy(self.computer_system_mockup)
        computer_system_mockup["Links"]["ResourceBlocks"].append(
            volume_resource_block)
        spt_uuid = "61c3a463-1355-4c68-a4e3-4f08c322af1b"
        volume_uri = ["/rest/storage-volumes/volume_uuid"]
        computer_system = ComputerSystem.build_composed_system(
            self.server_hardware,
            self.server_hardware_types,
            self.server_profile,
            [self.drives[4]],
            spt_uuid,
            self.manager_uuid,
            volume_uri
        )

        result = json.loads(computer_system.serialize())

        self.assertEqualMockup(computer_system_mockup, result)

    def test_build_physical_system(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ComputerSystemPhysicalType.json'
        ) as f:
            computer_system_mockup = json.load(f)

        computer_system = ComputerSystem.build_physical_system(
            self.server_hardware, self.manager_uuid
        )
        result = json.loads(computer_system.serialize())

        self.assertEqualMockup(computer_system_mockup, result)

    def test_build_server_profile(self):
        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplates.json'
        ) as f:
            spt = json.load(f)

        system_block = {
            "uuid": "FE50A6FE-B1AC-4E42-8D40-B73CA8CC0CD2"
        }

        computer_system = ComputerSystem.build_server_profile(
            "Composed System Using Redfish", "", spt[0], system_block,
            [], [], [])

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileBuiltFromTemplateToCreateASystem.json'
        ) as f:
            expected_server_profile_built = json.load(f)

        self.assertEqual(computer_system["name"],
                         expected_server_profile_built["name"])
