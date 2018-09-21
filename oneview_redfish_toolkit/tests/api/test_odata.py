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

import json

from oneview_redfish_toolkit.api.odata import Odata
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestOdata(BaseTest):
    """Tests for Odata class"""

    def test_class_instantiation(self):
        """Tests class instantiation and validation"""

        try:
            odata = Odata()
        except Exception as e:
            self.fail("Failed to instantiate Odata. Error: ".format(e))
        self.assertIsInstance(odata, Odata)

    def test_serialize(self):
        """Tests the serialize function result against known result"""

        odata = Odata()
        result = json.loads(odata.serialize())

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Odata.json'
        ) as f:
            odata_mockup = json.load(f)
        self.assertEqualMockup(odata_mockup, result)
