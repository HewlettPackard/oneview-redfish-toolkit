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
import unittest
from unittest import mock

# 3rd party libs
from flask import Flask
from flask import Response
from flask_api import status

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints import event_service
from oneview_redfish_toolkit import util


class TestEventService(unittest.TestCase):
    """Tests for EventService blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client):
        """Tests EventService blueprint setup"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(event_service.event_service)

        @self.app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        def internal_server_error(error):
            """General InternalServerError handler for the app"""

            redfish_error = RedfishError(
                "InternalError",
                "The request failed due to an internal service error.  "
                "The service is still operational.")
            redfish_error.add_extended_info("InternalError")
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype="application/json")

        @self.app.errorhandler(status.HTTP_400_BAD_REQUEST)
        def bad_request(error):
            """Creates a Bad Request Error response"""
            redfish_error = RedfishError(
                "PropertyValueNotInList", error.description)

            redfish_error.add_extended_info(
                message_id="PropertyValueNotInList",
                message_args=["VALUE", "PROPERTY"],
                related_properties=["PROPERTY"])

            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_400_BAD_REQUEST,
                mimetype='application/json')

        # creates a test client
        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch('oneview_redfish_toolkit.util.delivery_retry_attempts', 3)
    @mock.patch('oneview_redfish_toolkit.util.delivery_retry_interval', 30)
    def test_get_event_service(self):
        """Tests EventService blueprint result against know value"""

        response = self.app.get("/redfish/v1/EventService/")

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/EventService.json'
        ) as f:
            event_service_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(event_service_mockup, result)

    def test_post_submit_event_without_event_type(self):
        """Tests EventService SubmitTestEvent action without EventType"""

        response = self.app.post(
            '/redfish/v1/EventService/Actions''/EventService.SubmitTestEvent/')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('application/json', response.mimetype)

    def test_submit_event_with_invalid_event_type(self):
        """Tests EventService SubmitTestEvent action with invalid EventType"""

        response = self.app.post(
            '/redfish/v1/EventService/Actions''/EventService.SubmitTestEvent/',
            data='{"EventType": "INVALID"}',
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('application/json', response.mimetype)

    @mock.patch.object(util, 'dispatch_event')
    def test_submit_event_with_exception(self, dispatch_event_mock):
        """Tests SubmitTestEvent when dispatch_event raises an exception"""

        dispatch_event_mock.side_effect = Exception()

        response = self.app.post(
            '/redfish/v1/EventService/Actions''/EventService.SubmitTestEvent/',
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

        response = self.app.post(
            '/redfish/v1/EventService/Actions''/EventService.SubmitTestEvent/',
            data='{"EventType": "Alert"}',
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(self.alert_mockup, result)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('application/json', response.mimetype)
