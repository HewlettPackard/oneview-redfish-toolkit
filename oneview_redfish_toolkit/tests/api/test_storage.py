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

from oneview_redfish_toolkit.api.storage import Storage
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestStorage(BaseTest):
    """Tests for Storage class"""

    def setUp(self):
        """Tests preparation"""

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Storage.json'
        ) as f:
            self.storage_mockup = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwareTypes.json'
        ) as f:
            self.server_hardware_types = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'SASLogicalJBODListForStorage.json'
        ) as f:
            self.sas_logical_jbods = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        storage = Storage(self.server_profile,
                          self.server_hardware_types,
                          self.sas_logical_jbods)

        result = json.loads(storage.serialize())

        self.assertEqualMockup(self.storage_mockup, result)
