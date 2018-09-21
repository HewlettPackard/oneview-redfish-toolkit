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

"""
    Tests for manager_collection.py
"""

from collections import OrderedDict
import json

from oneview_redfish_toolkit.api.manager_collection \
    import ManagerCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestManagerCollection(BaseTest):
    """Tests for ManagerCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ManagerCollection result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ManagerCollection.json'
        ) as f:
            self.manager_collection_mockup = json.load(f)

        self.appliance_info_list = OrderedDict()
        self.appliance_info_list["10.0.0.1"] = \
            "b08eb206-a904-46cf-9172-dcdff2fa9639"
        self.appliance_info_list["10.0.0.2"] = \
            "c9ba5ca4-c1f8-48c7-9798-1e8b8897ef50"

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            manager_collection = ManagerCollection(
                self.appliance_info_list
            )
        except Exception as e:
            self.fail("Failed to instantiate ManagerCollection class."
                      " Error: {}".format(e))
        self.assertIsInstance(manager_collection, ManagerCollection)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            manager_collection = ManagerCollection(
                self.appliance_info_list
            )
        except Exception as e:
            self.fail("Failed to instantiate ManagerCollection class."
                      " Error: {}".format(e))

        try:
            result = json.loads(manager_collection.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqualMockup(self.manager_collection_mockup, result)
