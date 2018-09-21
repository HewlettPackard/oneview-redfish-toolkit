# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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

import collections

from oneview_redfish_toolkit.api.metadata import Metadata
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestOdata(BaseTest):
    """Tests for Metadata class"""

    def setUp(self):
        """Tests preparation"""
        self.schemas = collections.OrderedDict()
        self.schemas["ComputerSystemCollection"] = \
            "ComputerSystemCollection.json"
        self.schemas["ComputerSystem"] = "ComputerSystem.v1_4_0.json"

    def test_class_instantiation(self):
        """Tests class instantiation and validation"""

        try:
            metadata = Metadata(self.schemas)
        except Exception as e:
            self.fail("Failed to instantiate Metadata. Error: ".format(e))
        self.assertIsInstance(metadata, Metadata)

    def test_serialize(self):
        """Tests the serialize function result against known result"""

        metadata = Metadata(self.schemas)
        result = metadata.serialize()

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Metadata.xml'
        ) as f:
            metadata_mockup = f.read()
        self.assertEqualMockup(metadata_mockup, result)
