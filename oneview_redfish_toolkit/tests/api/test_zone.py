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
              'ServerHardwareList.json') as f:
        server_hardware_list = json.load(f)[:4]

    with open('oneview_redfish_toolkit/mockups/oneview/'
              'DrivesByDriveEnclosure.json') as f:
        drives_by_encl = json.load(f)
        drives = drives_by_encl["members"]

    with open('oneview_redfish_toolkit/mockups/redfish/Zone.json') as f:
        zone_mockup = json.load(f)

    with open('oneview_redfish_toolkit/mockups/redfish/'
              'ZoneWithoutDrives.json') as f:
        zone_without_drives_mockup = json.load(f)

        enclosure_name = "0000A66101"
        enclosure_name_none = None

    def test_drives_with_network_and_drive_links(self):
        """Tests when all is configured properly"""

        profile_template = copy.deepcopy(self.server_profile_template)
        zone_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66101"

        zone = Zone(zone_id,
                    profile_template,
                    self.server_hardware_list,
                    self.enclosure_name,
                    self.drives)
        result = json.loads(zone.serialize())

        self.assertEqualMockup(self.zone_mockup, result)

    def test_drives_as_links_when_storage_controllers_are_not_configured(self):
        """Tests Drives as Links when not configured

            Tests if Drive Resource blocks is empty when Storage Controllers
            are not configured
        """

        profile_template = copy.deepcopy(self.server_profile_template)
        profile_template["localStorage"]["controllers"] = []
        zone_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"

        zone = Zone(zone_id,
                    profile_template,
                    self.server_hardware_list,
                    self.enclosure_name_none,
                    self.drives)
        result = json.loads(zone.serialize())

        self.assertEqualMockup(self.zone_without_drives_mockup, result)

    def test_drives_as_links_when_storage_controller_is_embedded(self):
        """Tests Drives as Links when not configured properly

            Tests if Drive Resource blocks is empty when Storage Controllers
            are not configured properly for Redfish
        """

        profile_template = copy.deepcopy(self.server_profile_template)
        profile_template["localStorage"]["controllers"] = [{
            "deviceSlot": "Embedded",
            "mode": "HBA",
            "initialize": True,
            "driveWriteCache": "Unmanaged",
            "logicalDrives": None
        }]
        zone_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"

        zone = Zone(zone_id,
                    profile_template,
                    self.server_hardware_list,
                    self.enclosure_name_none,
                    self.drives)
        result = json.loads(zone.serialize())
        self.assertEqualMockup(self.zone_without_drives_mockup, result)

    def test_spt_when_connections_are_not_configured(self):
        """Tests Zone when connections are not set to Server Profile Template

            The Zone must have a NetworkResourceBlock even when connections
            are not set in SPT
        """

        profile_template = copy.deepcopy(self.server_profile_template)
        profile_template["connectionSettings"]["connections"] = []
        zone_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66101"

        zone = Zone(zone_id,
                    profile_template,
                    self.server_hardware_list,
                    self.enclosure_name,
                    self.drives)
        result = json.loads(zone.serialize())
        self.assertEqualMockup(self.zone_mockup, result)
