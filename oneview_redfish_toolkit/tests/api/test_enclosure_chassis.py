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
    def setUp(self, mock_ov):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading ov_enclosure mockup value
        with open(
            'oneview_redfish_toolkit/mockups/OneViewEnclosureChassis.json'
        ) as f:
            self.ov_enclosure = json.load(f)

        # Loading env_config mockup value
        with open(
                'oneview_redfish_toolkit/mockups/'
                'EnclosureEnvironmentalConfig.json'
        ) as f:
            self.env_config = json.load(f)

        # Loading rf_enclosure mockup result
        with open(
            'oneview_redfish_toolkit/mockups/RedfishEnclosureChassis.json'
        ) as f:
            self.rf_enclosure = f.read()

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = EnclosureChassis(self.ov_enclosure, self.env_config)
        except Exception as e:
            self.fail("Failed to instantiate Chassis class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, EnclosureChassis)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            obj = EnclosureChassis(self.ov_enclosure, self.env_config)
        except Exception as e:
            self.fail("Failed to instantiate Chassis class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(json_str, self.rf_enclosure)
