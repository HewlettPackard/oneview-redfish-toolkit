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

from oneview_redfish_toolkit.api.enclosure_manager import EnclosureManager
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestEnclosureManager(unittest.TestCase):
    """Tests for EnclosureManager class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading enclosure mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/Enclosure.json'
        ) as f:
            self.enclosure = json.load(f)

        # Loading enclosure_manager_mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/EnclosureManager.json'
        ) as f:
            self.enclosure_manager_mockup = f.read()

        self.oneview_version = "3.00.07-0288219"

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            enclosure_manager = EnclosureManager(
                self.enclosure,
                self.oneview_version
            )
        except Exception as e:
            self.fail("Failed to instantiate EnclosureManager class."
                      " Error: {}".format(e))
        self.assertIsInstance(enclosure_manager, EnclosureManager)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            enclosure_manager = EnclosureManager(
                self.enclosure,
                self.oneview_version
            )
        except Exception as e:
            self.fail("Failed to instantiate EnclosureManager class."
                      " Error: {}".format(e))

        try:
            json_str = enclosure_manager.serialize()
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.enclosure_manager_mockup, json_str)
