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

from oneview_redfish_toolkit.api.zone_collection import ZoneCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestZoneCollection(BaseTest):
    """Tests for ZoneCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerHardware list mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplates.json'
        ) as f:
            self.server_profile_templates = json.load(f)

        # Loading ZoneCollection result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/ZoneCollection.json'
        ) as f:
            self.zone_collection_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated
        try:
            zone_collection = ZoneCollection(self.server_profile_templates)
        except Exception as e:
            self.fail("Failed to instantiate ZoneCollection class."
                      " Error: {}".format(e))
        self.assertIsInstance(zone_collection, ZoneCollection)

    def test_serialize(self):
        # Tests the serialize function result against known result
        try:
            zone_collection = ZoneCollection(self.server_profile_templates)
        except Exception as e:
            self.fail("Failed to instantiate ZoneCollection class."
                      " Error: {}".format(e))

        try:
            result = json.loads(zone_collection.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqual(self.zone_collection_mockup, result)
