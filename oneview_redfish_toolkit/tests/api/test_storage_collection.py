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

from oneview_redfish_toolkit.api.storage_collection import StorageCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestStorageCollection(BaseTest):
    """Tests for StorageCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading StorageCollection mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageCollection.json'
        ) as f:
            self.storage_collection_mockup = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        storage_collection = \
            StorageCollection('b425802b-a6a5-4941-8885-aab68dfa2ee2')

        result = json.loads(storage_collection.serialize())

        self.assertEqualMockup(self.storage_collection_mockup, result)
