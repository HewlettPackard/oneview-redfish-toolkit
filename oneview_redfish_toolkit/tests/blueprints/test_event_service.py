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

# Python libs
import json
from unittest import mock

# 3rd party libs
from flask_api import status

# Module libs
from oneview_redfish_toolkit.blueprints import event_service
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest
from oneview_redfish_toolkit import util


class TestEventService(BaseFlaskTest):
    """Tests for EventService blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestEventService, self).setUpClass()

        self.app.register_blueprint(event_service.event_service)

    @mock.patch('oneview_redfish_toolkit.util.get_delivery_retry_attempts')
    @mock.patch('oneview_redfish_toolkit.util.get_delivery_retry_interval')
    def test_get_event_service(self, get_delivery_retry_interval,
                               get_delivery_retry_attempts):
        """Tests EventService blueprint result against known value"""
        get_delivery_retry_interval.return_value = 30
        get_delivery_retry_attempts.return_value = 3

        response = self.client.get("/redfish/v1/EventService/")

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/EventService.json'
        ) as f:
            event_service_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(event_service_mockup, result)

    def test_post_submit_event_without_event_type(self):
        """Tests EventService SubmitTestEvent action without EventType"""

        response = self.client.post(
            '/redfish/v1/EventService/Actions/EventService.SubmitTestEvent/')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('application/json', response.mimetype)

    def test_submit_event_with_invalid_event_type(self):
        """Tests EventService SubmitTestEvent action with invalid EventType"""

        response = self.client.post(
            '/redfish/v1/EventService/Actions/EventService.SubmitTestEvent/',
            data='{"EventType": "INVALID"}',
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('application/json', response.mimetype)

    @mock.patch.object(util, 'dispatch_event')
    def test_submit_event_with_exception(self, dispatch_event_mock):
        """Tests SubmitTestEvent when dispatch_event raises an exception"""

        dispatch_event_mock.side_effect = Exception()

        response = self.client.post(
            '/redfish/v1/EventService/Actions/EventService.SubmitTestEvent/',
            data='{"EventType": "Alert"}',
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    @mock.patch.object(util, 'dispatch_event')
    def test_submit_event_correct_response(self, dispatch_event_mock):
        """Tests SubmitTestEvent action with OneView SCMB alert"""

        # Loading Alert mockup value
        with open(
            'oneview_redfish_toolkit/mockups/redfish/Alert.json'
        ) as f:
            self.alert_mockup = json.load(f)

        response = self.client.post(
            '/redfish/v1/EventService/Actions''/EventService.SubmitTestEvent/',
            data='{"EventType": "Alert"}',
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqualMockup(self.alert_mockup, result)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertEqual('application/json', response.mimetype)
