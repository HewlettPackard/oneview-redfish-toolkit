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

    with open('oneview_redfish_toolkit/mockups/redfish/'
              'CapabilitiesObject.json') as f:
        capabilities_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        capabilities_obj = CapabilitiesObject(self.server_profile_template)

        self.assertIsInstance(capabilities_obj, CapabilitiesObject)

    def test_serialize(self):
        # Tests the serialize function result against known result
        capabilities_obj = CapabilitiesObject(self.server_profile_template)
        result = json.loads(capabilities_obj.serialize())

        self.assertEqualMockup(self.capabilities_mockup, result)
