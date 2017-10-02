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

from oneview_redfish_toolkit.api.enclosure_chassis import EnclosureChassis
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestEnclosureChassis(unittest.TestCase):
    """Tests for Chassis class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mock):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading enclosure mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/Enclosure.json'
        ) as f:
            self.enclosure = json.load(f)

        # Loading environment_config mockup value
        with open(
                'oneview_redfish_toolkit/mockups_oneview/'
                'EnclosureEnvironmentalConfig.json'
        ) as f:
            self.environment_config = json.load(f)

        # Loading enclosure_mockup mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/EnclosureChassis.json'
        ) as f:
            self.enclosure_mockup = f.read()

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            enclosure_chassis = EnclosureChassis(
                self.enclosure,
                self.environment_config
            )
        except Exception as e:
            self.fail("Failed to instantiate Chassis class."
                      " Error: {}".format(e))
        self.assertIsInstance(enclosure_chassis, EnclosureChassis)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            enclosure_chassis = EnclosureChassis(
                self.enclosure,
                self.environment_config
            )
        except Exception as e:
            self.fail("Failed to instantiate Chassis class."
                      " Error: {}".format(e))

        try:
            json_str = enclosure_chassis.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.enclosure_mockup, json_str)
