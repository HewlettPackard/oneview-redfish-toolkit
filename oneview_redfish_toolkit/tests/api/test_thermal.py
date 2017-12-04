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

from oneview_redfish_toolkit.api.thermal import Thermal
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestThermal(unittest.TestCase):
    """Tests for Thermal class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading OneView SH Utilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardwareUtilization.json'
        ) as f:
            self.server_hardware_utilization = json.load(f)

        # Loading BladeChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/BladeChassisThermal.json'
        ) as f:
            self.blade_thermal_mockup = f.read()

        # Loading OneView Enclosure Utilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/EnclosureUtilization.json'
        ) as f:
            self.enclosure_utilization = json.load(f)

        # Loading EnclosureChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EnclosureChassisThermal.json'
        ) as f:
            self.enclosure_thermal_mockup = f.read()

        # Loading OneView Rack Topology mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/RackDeviceTopology.json'
        ) as f:
            self.rack_utilization = json.load(f)

        # Loading RackChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/RackChassisThermal.json'
        ) as f:
            self.rack_thermal_mockup = f.read()

    def test_class_instantiation_for_blade(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = Thermal(self.server_hardware_utilization, 'uuid', 'Blade')
        except Exception as e:
            self.fail("Failed to instantiate Thermal class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, Thermal)

    def test_class_instantiation_for_enclosure(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = Thermal(self.enclosure_utilization, 'uuid', 'Enclosure')
        except Exception as e:
            self.fail("Failed to instantiate Thermal class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, Thermal)

    def test_class_instantiation_for_rack(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = Thermal(self.rack_utilization, 'uuid', 'Rack')
        except Exception as e:
            self.fail("Failed to instantiate Thermal class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, Thermal)

    def test_serialize_for_blade(self):
        # Tests the serialize function result against known result

        try:
            obj = Thermal(
                self.server_hardware_utilization,
                "36343537-3338-4448-3538-4E5030333434",
                "Blade")
        except Exception as e:
            self.fail("Failed to instantiate Thermal class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.blade_thermal_mockup, json_str)

    def test_serialize_for_enclosure(self):
        # Tests the serialize function result against known result

        try:
            obj = Thermal(
                self.enclosure_utilization,
                "0000000000A66101",
                "Enclosure")
        except Exception as e:
            self.fail("Failed to instantiate Thermal class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.enclosure_thermal_mockup, json_str)

    def test_serialize_for_rack(self):
        # Tests the serialize function result against known result

        try:
            obj = Thermal(
                self.rack_utilization,
                "2AB100LMNB",
                "Rack")
        except Exception as e:
            self.fail("Failed to instantiate Thermal class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

            self.assertEqual(self.rack_thermal_mockup, json_str)
