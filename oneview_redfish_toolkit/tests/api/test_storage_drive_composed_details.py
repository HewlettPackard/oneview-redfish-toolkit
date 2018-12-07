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
import copy

from oneview_redfish_toolkit.api.drive import Drive
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestDrive(BaseTest):
    """Tests for api/Drive class"""

    def setUp(self):
        """Tests preparation"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drive.json'
        ) as f:
            self.drive = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'SASLogicalJBODListForStorage.json'
        ) as f:
            self.sas_logical_jbods = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/DriveEnclosure.json'
        ) as f:
            self.drive_enclosure = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'DriveWithMediaTypeNull.json'
        ) as f:
            self.drive_with_mediaType_null = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'DriveForRBWithMediaTypeNull.json'
        ) as f:
            self.drive_with_mediaType_null_rb = json.load(f)

    def test_build_for_computer_system(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/Drive.json'
        ) as f:
            expected_result = json.load(f)

        target = Drive.build_for_computer_system(4,
                                                 self.server_profile,
                                                 self.sas_logical_jbods[1])

        result = json.loads(target.serialize())

        self.assertEqualMockup(expected_result, result)

    def test_build_for_resource_block(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/DriveForResourceBlock.json'
        ) as f:
            expected_result = json.load(f)

        target = Drive.build_for_resource_block(self.drive,
                                                self.drive_enclosure)
        result = json.loads(target.serialize())

        self.assertEqualMockup(expected_result, result)

    def test_build_for_composed_system_with_unknown_mediaType(self):

        sas_logical_jbods = copy.deepcopy(self.sas_logical_jbods[1])

        sas_logical_jbods["driveTechnology"]["driveMedia"] = "Unknown"

        drive = Drive.build_for_computer_system("4", self.server_profile,
                                                sas_logical_jbods)

        result = json.loads(drive.serialize())

        self.assertEqualMockup(self.drive_with_mediaType_null, result)

    def test_build_for_resource_block_with_unknown_mediaType(self):

        drive = copy.deepcopy(self.drive)

        drive["attributes"]["mediaType"] = "Unknown"

        drive = Drive.build_for_resource_block(drive,
                                               self.drive_enclosure)

        result = json.loads(drive.serialize())

        self.assertEqualMockup(self.drive_with_mediaType_null_rb, result)
