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

from oneview_redfish_toolkit.api.capability import Capability
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestCapability(BaseTest):
    """Tests for Capability class"""

    with open('oneview_redfish_toolkit/mockups/oneview/'
              'ServerProfileTemplate.json') as f:
        server_profile_template = json.load(f)

    with open('oneview_redfish_toolkit/mockups/redfish/Capability.json') as f:
        capability_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        try:
            capability = Capability(self.server_profile_template)
        except Exception as e:
            self.fail("Failed to instantiate Capability class."
                      " Error: {}".format(e))
        self.assertIsInstance(capability, Capability)

    def test_serialize(self):
        # Tests the serialize function result against known result
        try:
            capability = Capability(self.server_profile_template)
        except Exception as e:
            self.fail("Failed to instantiate Capability class."
                      " Error: {}".format(e))

        try:
            result = json.loads(capability.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqual(self.capability_mockup, result)
