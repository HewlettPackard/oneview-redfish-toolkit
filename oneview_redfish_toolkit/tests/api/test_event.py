# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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

from oneview_redfish_toolkit.api.event import Event
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestEvent(BaseTest):
    """Tests for Event class"""

    def setUp(self):
        """Tests preparation"""

        # Loading Alert mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            self.alert = json.load(f)

        # Loading Event mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/Alert.json'
        ) as f:
            self.event_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            event = Event(self.alert)
        except Exception as e:
            self.fail("Failed to instantiate Event class."
                      " Error: {}".format(e))
        self.assertIsInstance(event, Event)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            event = Event(self.alert)
        except Exception as e:
            self.fail("Failed to instantiate Event class."
                      " Error: {}".format(e))

        try:
            result = json.loads(event.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: {}".format(e))

        self.assertEqualMockup(self.event_mockup, result)
