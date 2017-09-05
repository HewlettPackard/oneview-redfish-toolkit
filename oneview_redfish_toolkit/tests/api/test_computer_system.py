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

import json

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestComputerSystem(unittest.TestCase):
    """Tests for ComputerSystem class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, mock_ov):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('oneview_redfish_toolkit/redfish.ini')

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/ServerHardware.json'
        ) as f:
            self.sh_dict = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
            'oneview_redfish_toolkit/mockups/ServerHardwareTypes.json'
        ) as f:
            self.sht_dict = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups/ComputerSystem.json'
        ) as f:
            self.computer_system = f.read()

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = ComputerSystem(self.sh_dict, self.sht_dict)
        except Exception as e:
            self.fail("Failed to instantiate ComputerSystem class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, ComputerSystem)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            obj = ComputerSystem(self.sh_dict, self.sht_dict)
        except Exception as e:
            self.fail("Failed to instantiate ComputerSystem class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(json_str, self.computer_system)
