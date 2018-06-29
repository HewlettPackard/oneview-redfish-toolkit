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
import copy
import json

from oneview_redfish_toolkit.api.zone import Zone
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestZone(BaseTest):
    """Tests for Zone class"""

    with open('oneview_redfish_toolkit/mockups/oneview/'
              'ServerProfileTemplate.json') as f:
        server_profile_template = json.load(f)

    with open('oneview_redfish_toolkit/mockups/oneview/'
              'AvailableTargetsForSPT.json') as f:
        available_targets = json.load(f)

    with open('oneview_redfish_toolkit/mockups/oneview/'
              'Drives.json') as f:
        drives = json.load(f)

    with open('oneview_redfish_toolkit/mockups/redfish/Zone.json') as f:
        zone_mockup = json.load(f)

    with open('oneview_redfish_toolkit/mockups/redfish/'
              'ZoneWithoutDrives.json') as f:
        zone_without_drives_mockup = json.load(f)

    def test_serialize(self):
        zone = Zone(self.server_profile_template,
                    self.available_targets,
                    self.drives)
        result = json.loads(zone.serialize())

        self.assertEqual(self.zone_mockup, result)

    def test_drives_as_links_when_storage_controllers_are_not_configured(
            self):
        profile_template = copy.deepcopy(self.server_profile_template)
        profile_template["localStorage"]["controllers"] = []

        zone = Zone(profile_template,
                    self.available_targets,
                    self.drives)
        result = json.loads(zone.serialize())

        self.assertEqual(self.zone_without_drives_mockup, result)

    def test_drives_as_links_when_storage_controller_is_embedded(self):
        profile_template = copy.deepcopy(self.server_profile_template)
        profile_template["localStorage"]["controllers"] = [{
            "deviceSlot": "Embedded",
            "mode": "HBA",
            "initialize": True,
            "driveWriteCache": "Unmanaged",
            "logicalDrives": None
        }]

        zone = Zone(profile_template,
                    self.available_targets,
                    self.drives)
        result = json.loads(zone.serialize())

        self.assertEqual(self.zone_without_drives_mockup, result)
