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

# Python libs
import json
import unittest
from unittest import mock

# 3rd party libs

# Own project libs
from oneview_redfish_toolkit.api.rack_chassis import RackChassis
from oneview_redfish_toolkit import util


class TestRackChassis(unittest.TestCase):
    """Tests for Chassis class

        Tests:
            - Rack chassis instantiation
            - Rack chassis serialize
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, mock_ov):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading ov_rack mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/Rack.json'
        ) as f:
            self.ov_rack = json.load(f)

        # Loading rf_rack mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/RackChassis.json'
        ) as f:
            self.rf_rack = f.read()

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            obj = RackChassis(self.ov_rack)
        except Exception as e:
            self.fail("Failed to instantiate RackChassis class."
                      " Error: {}".format(e))
        self.assertIsInstance(obj, RackChassis)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            obj = RackChassis(self.ov_rack)
        except Exception as e:
            self.fail("Failed to instantiate RackChassis class."
                      " Error: {}".format(e))

        try:
            json_str = obj.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(json_str, self.rf_rack)
