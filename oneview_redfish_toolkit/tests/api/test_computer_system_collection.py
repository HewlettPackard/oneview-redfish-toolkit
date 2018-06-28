# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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
    Tests for computer_system_collection.py
"""

import json

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestComputerSystemCollection(BaseTest):
    """Tests for ComputerSystemCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerHardware list mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardwaresProfiledApplied.json'
        ) as f:
            self.server_hardware_list = json.load(f)

        # Loading ComputerSystemCollection result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ComputerSystemCollection.json'
        ) as f:
            self.computer_system_collection_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            computer_system_collection = ComputerSystemCollection(
                self.server_hardware_list
            )
        except Exception as e:
            self.fail("Failed to instantiate ComputerSystemCollection class."
                      " Error: {}".format(e))
        self.assertIsInstance(
            computer_system_collection,
            ComputerSystemCollection
        )

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            computer_system_collection = ComputerSystemCollection(
                self.server_hardware_list
            )
        except Exception as e:
            self.fail("Failed to instantiate ComputerSystemCollection class."
                      " Error: {}".format(e))

        try:
            result = json.loads(computer_system_collection.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqual(self.computer_system_collection_mockup, result)
