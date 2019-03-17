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

from oneview_redfish_toolkit.api.storage_resource_block import \
    StorageResourceBlock
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestStorageResourceBlock(BaseTest):
    """Tests for StorageResourceBlock class"""

    @classmethod
    def setUpClass(self):
        """Tests preparation"""

        super(TestStorageResourceBlock, self).setUpClass()

        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/StorageResourceBlock.json'
        ) as f:
            self.resource_block_mockup = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drive.json'
        ) as f:
            self.drive = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/DriveIndexTrees.json'
        ) as f:
            self.drive_index_tree = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ExternalStorageResourceBlock.json'
        ) as f:
            self.external_storage_rb_mockup = json.load(f)

        with open('oneview_redfish_toolkit/mockups/oneview/'
                  'Volumes.json') as f:
            volumes = json.load(f)
            self.volume = volumes[0]

    def test_serialize(self):
        zone_ids = [
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66101",
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66102",
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66103",
            "75871d70-789e-4cf9-8bc8-6f4d73193578",
        ]

        resource_block = StorageResourceBlock(
            self.drive, self.drive_index_tree, zone_ids, None)
        result = json.loads(resource_block.serialize())

        self.assertEqualMockup(self.resource_block_mockup, result)

    def test_when_server_profile_template_has_not_storage_controller(self):
        """This test is a invalid state (it should never occur)

            The Drive ever must have at least one Zone
        """
        expected_result = copy.copy(self.resource_block_mockup)
        expected_result["Links"]["Zones"] = []

        zone_ids = ["75871d70-789e-4cf9-8bc8-6f4d73193578"]

        resource_block = StorageResourceBlock(
            self.drive, self.drive_index_tree, zone_ids, None)
        result = json.loads(resource_block.serialize())

        self.assertEqualMockup(self.resource_block_mockup, result)

    def test_external_storage_resource_block(self):
        zone_ids = ["5394236a-384b-4151-9e32-685dbe990e93"]
        server_profiles = [
            "/rest/server-profiles/72d7f1ff-00e5-43b6-83c2-d4d61abd1708",
            "/rest/server-profiles/416c23ad-1587-4484-9174-e10afd1801f9"
        ]

        resource_block = StorageResourceBlock(
            self.volume, None, zone_ids, server_profiles)
        result = json.loads(resource_block.serialize())

        self.assertEqualMockup(self.external_storage_rb_mockup, result)

    def test_external_storage_resource_block_with_empty_sp_list(self):
        zone_ids = ["5394236a-384b-4151-9e32-685dbe990e93"]
        expected_resource_block = copy.deepcopy(
            self.external_storage_rb_mockup)
        expected_resource_block["Links"]["ComputerSystems"] = []
        resource_block = StorageResourceBlock(
            self.volume, None, zone_ids, [])
        result = json.loads(resource_block.serialize())

        self.assertEqual(expected_resource_block["Name"], result["Name"])
        self.assertEqual(expected_resource_block["Id"], result["Id"])

    def test_private_storage_volume_resource_block(self):
        zone_ids = ["5394236a-384b-4151-9e32-685dbe990e93"]
        server_profiles = [
            "/rest/server-profiles/72d7f1ff-00e5-43b6-83c2-d4d61abd1708",
            "/rest/server-profiles/416c23ad-1587-4484-9174-e10afd1801f9"
        ]
        volume = copy.deepcopy(self.volume)
        volume["isShareable"] = False
        external_storage_rb_mockup = copy.deepcopy(
            self.external_storage_rb_mockup)
        external_storage_rb_mockup["CompositionStatus"]["CompositionState"] = \
            "Composed"
        external_storage_rb_mockup["CompositionStatus"]["SharingCapable"] = \
            False

        resource_block = StorageResourceBlock(
            volume, None, zone_ids, server_profiles)
        result = json.loads(resource_block.serialize())

        self.assertEqualMockup(external_storage_rb_mockup, result)
