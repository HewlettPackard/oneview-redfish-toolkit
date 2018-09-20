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

"""
    Tests for computer_system_collection.py
"""

import json

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestComputerSystemCollection(BaseTest):
    """Tests for ComputerSystemCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerHardware list mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardwareListWithServerProfileApplied.json'
        ) as f:
            self.server_hardware_list = json.load(f)

        # Loading ComputerSystemCollection result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ComputerSystemCollection.json'
        ) as f:
            self.computer_system_collection_mockup = json.load(f)

        # Loading ServerProfileTemplates result mockup
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplates.json'
        ) as f:
            self.server_profile_template_list = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        zone_ids = [
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66101",
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66102",
            "75871d70-789e-4cf9-8bc8-6f4d73193578"
        ]

        computer_system_collection = ComputerSystemCollection(
            self.server_hardware_list,
            self.server_profile_template_list,
            zone_ids
        )

        result = json.loads(computer_system_collection.serialize())

        self.assertEqualMockup(self.computer_system_collection_mockup, result)
