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

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        resource_block = StorageResourceBlock(self.drive)

        self.assertIsInstance(resource_block, StorageResourceBlock)

    def test_serialize(self):
        # Tests the serialize function result against known result
        resource_block = StorageResourceBlock(self.drive)
        result = json.loads(resource_block.serialize())

        self.assertEqual(self.resource_block_mockup, result)
