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

    @classmethod
    def setUpClass(self):
        super(TestProcessor, self).setUpClass()

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

    def test_serialize(self):
        # Tests the serialize function result against known result
        processor = Processor(self.server_hardware, '1')

        result = json.loads(processor.serialize())

        self.assertEqualMockup(self.processor_mockup, result)
