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

from oneview_redfish_toolkit.api.server_profile_template_resource_block \
    import ServerProfileTemplateResourceBlock
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestServerProfileTemplateResourceBlock(BaseTest):
    """Tests for ServerProfileTemplateResourceBlock class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerProfileTemplateResourceBlock mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ServerProfileTemplateResourceBlock.json'
        ) as f:
            self.resource_block_mockup = json.load(f)

        # Loading ServerProfileTemplate mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplate.json'
        ) as f:
            self.server_profile_template = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        try:
            resource_block = ServerProfileTemplateResourceBlock(
                '1f0ca9ef-7f81-45e3-9d64-341b46cf87e0',
                self.server_profile_template)
        except Exception as e:
            self.fail(
                "Failed to instantiate ServerProfileTemplateResourceBlock"
                " class. Error: {}".format(e))

        self.assertIsInstance(
            resource_block, ServerProfileTemplateResourceBlock)

    def test_serialize(self):
        # Tests the serialize function result against known result
        try:
            resource_block = ServerProfileTemplateResourceBlock(
                '1f0ca9ef-7f81-45e3-9d64-341b46cf87e0',
                self.server_profile_template)
        except Exception as e:
            self.fail(
                "Failed to instantiate ServerProfileTemplateResourceBlock"
                "  class. Error: {}".format(e))
        try:
            result = json.loads(resource_block.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqual(self.resource_block_mockup, result)
