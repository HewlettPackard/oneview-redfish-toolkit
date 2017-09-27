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

from oneview_redfish_toolkit.api.blade_manager import BladeManager
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestBladeManager(unittest.TestCase):
    """Tests for BladeManager class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, mock_ov):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/ServerHardware.json'
        ) as f:
            self.sh_dict = json.load(f)

        # Loading BladeManager mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/BladeManager.json'
        ) as f:
            self.blade_manager = f.read()

        self.ov_version = "3.00.07-0288219"

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = BladeManager(self.sh_dict, self.ov_version)
        except Exception as e:
            self.fail("Failed to instantiate BladeManager class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, BladeManager)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            obj = BladeManager(self.sh_dict, self.ov_version)
        except Exception as e:
            self.fail("Failed to instantiate BladeManager class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(json_str, self.blade_manager)
