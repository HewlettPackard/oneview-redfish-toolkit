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

    def test_serialize(self):
        # Tests the serialize function result against known result

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileTemplate.json'
        ) as f:
            server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ServerProfileTemplateResourceBlock.json'
        ) as f:
            expected_result = json.load(f)

        zone_ids = [
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66101",
            "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66102"
        ]

        resource_block = ServerProfileTemplateResourceBlock(
            '1f0ca9ef-7f81-45e3-9d64-341b46cf87e0',
            server_profile_template,
            zone_ids)

        result = json.loads(resource_block.serialize())

        self.assertEqualMockup(expected_result, result)

    def test_serialize_with_only_one_zone(self):
        # Tests the serialize function result against known result

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileTemplates.json'
        ) as f:
            server_profile_template = json.load(f)[1]

        with open(
                'oneview_redfish_toolkit/mockups/redfish'
                '/SPTResourceBlockWithOnlyOneZone.json'
        ) as f:
            expected_result = json.load(f)

        zone_ids = [
            expected_result["Id"]
        ]

        resource_block = ServerProfileTemplateResourceBlock(
            expected_result["Id"],
            server_profile_template,
            zone_ids)

        result = json.loads(resource_block.serialize())

        self.assertEqualMockup(expected_result, result)
