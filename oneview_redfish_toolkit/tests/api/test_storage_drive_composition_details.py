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

from oneview_redfish_toolkit.api.storage_drive_composition_details import \
    StorageDriveCompositionDetails
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestStorageDriveCompositionDetails(BaseTest):
    """Tests for StorageDriveCompositionDetails class"""

    def setUp(self):
        """Tests preparation"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drive.json'
        ) as f:
            self.drive = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/DriveEnclosure.json'
        ) as f:
            self.drive_enclosure = json.load(f)

    def test_serialize(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/StorageDriveCompositionDetails.json'
        ) as f:
            expected_result = json.load(f)

        target = StorageDriveCompositionDetails(self.drive,
                                                self.drive_enclosure)
        result = json.loads(target.serialize())

        self.assertEqualMockup(expected_result, result)
