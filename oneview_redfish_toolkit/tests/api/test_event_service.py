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
    Tests for event_service.py
"""

import json

from oneview_redfish_toolkit.api.event_service import EventService
from oneview_redfish_toolkit import util

import unittest
from unittest import mock


class TestEventService(unittest.TestCase):
    """Tests for EventService class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, mock_ov):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # Loading EventService result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EventService.json'
        ) as f:
            self.event_service_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            event_service = EventService()
        except Exception as e:
            self.fail("Failed to instantiate EventService class."
                      " Error: {}".format(e))
        self.assertIsInstance(event_service, EventService)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            manager_collection = EventService()
        except Exception as e:
            self.fail("Failed to instantiate EventService class."
                      " Error: {}".format(e))

        try:
            result = json.loads(manager_collection.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqual(self.event_service_mockup, result)
