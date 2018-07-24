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

from oneview_redfish_toolkit.api.composition_service import CompositionService
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestCompositionService(BaseTest):
    """Tests for CompositionService class"""

    def setUp(self):
        """Tests preparation"""

        # Loading CompositionService mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/CompositionService.json'
        ) as f:
            self.composition_service_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated

        try:
            compostion_service = CompositionService()
        except Exception as e:
            self.fail("Failed to instantiate CompositionService class."
                      " Error: {}".format(e))
        self.assertIsInstance(compostion_service, CompositionService)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            compostion_service = CompositionService()
        except Exception as e:
            self.fail("Failed to instantiate CompositionService class."
                      " Error: {}".format(e))

        try:
            expected_result = json.loads(compostion_service.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqualMockup(self.composition_service_mockup,
                               expected_result)
