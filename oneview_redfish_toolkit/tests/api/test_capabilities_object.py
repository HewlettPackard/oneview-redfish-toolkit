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

from oneview_redfish_toolkit.api.capabilities_object import CapabilitiesObject
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestCapabilitiesObject(BaseTest):
    """Tests for CapabilitiesObject class"""

    with open('oneview_redfish_toolkit/mockups/oneview/'
              'ServerProfileTemplate.json') as f:
        server_profile_template = json.load(f)

    def test_serialize_passing_spt_id_as_resource_id(self):
        # Tests the serialize using template id as resource_id

        with open('oneview_redfish_toolkit/mockups/redfish/'
                  'CapabilitiesObject.json') as f:
            capabilities_mockup = json.load(f)

        resource_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
        capabilities_obj = CapabilitiesObject(resource_id,
                                              self.server_profile_template)
        result = json.loads(capabilities_obj.serialize())

        self.assertEqualMockup(capabilities_mockup, result)

    def test_serialize_passing_spt_id_and_encl_id_as_resource_id(self):
        # Tests the serialize using template id + enclosure id as resource_id

        with open('oneview_redfish_toolkit/mockups/redfish/'
                  'CapabilitiesObjectWithSPTIdAndEnclId.json') as f:
            capabilities_mockup = json.load(f)

        resource_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0-0000000000A66101"
        capabilities_obj = CapabilitiesObject(resource_id,
                                              self.server_profile_template)
        result = json.loads(capabilities_obj.serialize())

        self.assertEqualMockup(capabilities_mockup, result)
