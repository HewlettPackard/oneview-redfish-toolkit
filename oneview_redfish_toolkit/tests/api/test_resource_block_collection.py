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

from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestResourceBlockCollection(BaseTest):
    """Tests for ResourceBlockCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerHardware list mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardwareList.json'
        ) as f:
            self.server_hardware_list = json.load(f)

        # Loading ServerProfileTemplate list mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplates.json'
        ) as f:
            self.server_profile_template_list = json.load(f)

        # Loading Drives list mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Drives.json'
        ) as f:
            self.drives_list = json.load(f)

        # Loading ResourceBlockCollection result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ResourceBlockCollection.json'
        ) as f:
            self.resource_block_collection_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        try:
            resource_block_collection = ResourceBlockCollection(
                self.server_hardware_list,
                self.server_profile_template_list,
                self.drives_list)
        except Exception as e:
            self.fail("Failed to instantiate ResourceBlockCollection class."
                      " Error: {}".format(e))
        self.assertIsInstance(
            resource_block_collection, ResourceBlockCollection)

    def test_serialize(self):
        # Tests the serialize function result against known result
        try:
            resource_block_collection = ResourceBlockCollection(
                self.server_hardware_list,
                self.server_profile_template_list,
                self.drives_list)
        except Exception as e:
            self.fail("Failed to instantiate ResourceBlockCollection class."
                      " Error: {}".format(e))

        try:
            result = json.loads(resource_block_collection.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqualMockup(self.resource_block_collection_mockup, result)

    def test_serialize_empty_result(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ResourceBlockCollectionEmpty.json'
        ) as f:
            expected_result = json.load(f)

        # Tests the serialize function result against empty list result
        resource_block_collection = ResourceBlockCollection()
        result = json.loads(resource_block_collection.serialize())

        self.assertEqualMockup(expected_result, result)
