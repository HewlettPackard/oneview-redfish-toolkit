# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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

from unittest import mock

from oneview_redfish_toolkit.api.event import Event
from oneview_redfish_toolkit.api.subscription import Subscription
from oneview_redfish_toolkit.event_dispatcher import EventDispatcher
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestEventDispatcher(BaseTest):
    """Tests for event_dispatcher.py"""

    @mock.patch('http.client.HTTPConnection.request')
    @mock.patch('logging.exception')
    def test_dispatch_event(self, exception_mock, request_mock):
        """Tests dispatch event"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            event_mockup = json.loads(f.read())

            event = Event(event_mockup)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/EventDestination.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

            subscription = Subscription(
                subscription_mockup['Id'],
                subscription_mockup['Destination'],
                subscription_mockup['EventTypes'],
                subscription_mockup['Context'])

        dispatcher = EventDispatcher(event, subscription, 1, 1)

        dispatcher.run()

        self.assertTrue(request_mock.called)
        self.assertFalse(exception_mock.called)

    @mock.patch.object(Event, 'serialize')
    @mock.patch('http.client.HTTPConnection.request')
    @mock.patch('logging.exception')
    def test_dispatch_event_serialization_fail(
        self, exception_mock, request_mock, serialize_mock):
        """Tests dispatch event with serialization fail"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            event_mockup = json.loads(f.read())

            event = Event(event_mockup)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/EventDestination.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

            subscription = Subscription(
                subscription_mockup['Id'],
                subscription_mockup['Destination'],
                subscription_mockup['EventTypes'],
                subscription_mockup['Context'])

        dispatcher = EventDispatcher(event, subscription, 1, 1)

        serialize_mock.side_effect = Exception()

        dispatcher.run()

        self.assertFalse(request_mock.called)
        self.assertTrue(exception_mock.called)

    @mock.patch('time.sleep')
    @mock.patch('http.client.HTTPConnection.request')
    @mock.patch('logging.exception')
    def test_dispatch_event_request_fail(
        self, exception_mock, request_mock, sleep_mock):
        """Tests dispatch event with request fail"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            event_mockup = json.loads(f.read())

            event = Event(event_mockup)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/EventDestination.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

            subscription = Subscription(
                subscription_mockup['Id'],
                subscription_mockup['Destination'],
                subscription_mockup['EventTypes'],
                subscription_mockup['Context'])

        dispatcher = EventDispatcher(event, subscription, 1, 1)

        request_mock.side_effect = Exception()

        dispatcher.run()

        sleep_mock.assert_called_with(1)
        self.assertTrue(exception_mock.called)
