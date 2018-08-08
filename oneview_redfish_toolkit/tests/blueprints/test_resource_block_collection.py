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

# Python libs
import json

# 3rd party libs
from flask_api import status

# Module libs
from oneview_redfish_toolkit.blueprints import resource_block_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestResourceBlockCollection(BaseFlaskTest):
    """Tests for ResourceBlockCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestResourceBlockCollection, self).setUpClass()

        self.app.register_blueprint(
            resource_block_collection.resource_block_collection)

    def test_get_resource_block_collection(self):
        """Tests ResourceBlockCollection"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwareList.json'
        ) as f:
            server_hardware_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplates.json'
        ) as f:
            server_profile_template_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drives.json'
        ) as f:
            drives_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ResourceBlockCollection.json'
        ) as f:
            resource_block_collection_mockup = json.load(f)

        self.oneview_client.server_hardware.get_all.return_value = \
            server_hardware_list

        self.oneview_client.server_profile_templates.get_all.return_value = \
            server_profile_template_list

        self.oneview_client.index_resources.get_all.return_value = \
            drives_list

        # Get ResourceBlockCollection
        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(resource_block_collection_mockup, result)

    def test_get_resource_block_collection_empty(self):
        """Tests ResourceBlockCollection with an empty list"""

        self.oneview_client.server_hardware.get_all.return_value = []
        self.oneview_client.server_profile_templates.get_all.return_value = []
        self.oneview_client.index_resources.get_all.return_value = []

        # Get ResourceBlockCollection
        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ResourceBlockCollectionEmpty.json'
        ) as f:
            expected_result = json.load(f)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_result, result)
