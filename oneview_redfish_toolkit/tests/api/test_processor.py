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

from oneview_redfish_toolkit.api.processor import Processor
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestProcessor(BaseTest):
    """Tests for Processor class"""

    def setUp(self):
        """Tests preparation"""

        # Loading Processor mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/Processor.json'
        ) as f:
            self.processor_mockup = json.load(f)

        # Loading ServerHardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        try:
            processor = Processor(
                '30303437-3034-4D32-3230-313133364752',
                '1', self.server_hardware)
        except Exception as e:
            self.fail("Failed to instantiate Processor class."
                      " Error: {}".format(e))
        self.assertIsInstance(processor, Processor)

    def test_serialize(self):
        # Tests the serialize function result against known result
        try:
            processor = Processor(
                '30303437-3034-4D32-3230-313133364752',
                '1', self.server_hardware)
        except Exception as e:
            self.fail("Failed to instantiate Processor class."
                      " Error: {}".format(e))

        try:
            result = json.loads(processor.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqual(self.processor_mockup, result)
