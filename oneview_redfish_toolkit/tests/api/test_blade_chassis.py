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

from oneview_redfish_toolkit.api.blade_chassis import BladeChassis
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestBladeChassis(unittest.TestCase):
    """Tests for Chassis class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mock):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading Chassis mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/BladeChassis.json'
        ) as f:
            self.blade_chassis_mockup = f.read()

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            blade_chassis = BladeChassis(self.server_hardware)
        except Exception as e:
            self.fail("Failed to instantiate Chassis class."
                      " Error: {}".format(e))
        self.assertIsInstance(blade_chassis, BladeChassis)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            blade_chassis = BladeChassis(self.server_hardware)
        except Exception as e:
            self.fail("Failed to instantiate Chassis class."
                      " Error: {}".format(e))

        try:
            json_str = blade_chassis.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.blade_chassis_mockup, json_str)
