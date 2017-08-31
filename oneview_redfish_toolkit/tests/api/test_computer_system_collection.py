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
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestComputerSystemCollection(unittest.TestCase):
    """Tests for ComputerSystemCollection class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, mock_ov):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('oneview_redfish_toolkit/redfish.ini')

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/'
            'ServerHardwares.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading ComputerSystemCollection result mockup
        with open(
            'oneview_redfish_toolkit/mockups/'
            'ComputerSystemCollection.json'
        ) as f:
            self.computer_system_collection = f.read()

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = ComputerSystemCollection(self.server_hardware)
        except Exception as e:
            self.fail("Failed to instanciate ComputerSystemCollection class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, ComputerSystemCollection)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            obj = ComputerSystemCollection(self.server_hardware)
        except Exception as e:
            self.fail("Failed to instanciate ComputerSystemCollection class")

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        with open(
            'oneview_redfish_toolkit/mockups/'
            'ComputerSystemCollection.json'
        ) as f:
            mok_json_result = f.read()

        self.assertEqual(json_str, mok_json_result)
