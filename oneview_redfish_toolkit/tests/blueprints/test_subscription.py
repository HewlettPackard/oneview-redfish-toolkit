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
from flask import Flask
from flask import Response
from flask_api import status

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints.subscription import subscription
from oneview_redfish_toolkit import util


class TestSubscription(unittest.TestCase):
    """Tests for Subscription blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client):
        """Tests Subscription blueprint setup"""

        # Loading variable in util module
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(subscription)

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

    @mock.patch('uuid.uuid1')
    def test_add_subscription(self, uuid_mockup):
        """Test POST Subscription"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.app.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "StatusChange"])),
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/Subscription.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(subscription_mockup, result)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_key1(self, uuid_mockup):
        """Test POST Subscription with invalid Destination key"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.app.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                INVALID="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "StatusChange"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_key2(self, uuid_mockup):
        """Test POST Subscription with invalid EventTypes key"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.app.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                INVALID=["Alert", "StatusChange"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_events(self, uuid_mockup):
        """Test POST Subscription with invalid EventTypes"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.app.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["INVALID"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_with_context(self, uuid_mockup):
        """Test POST Subscription with a Context"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.app.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert"],
                Context="WebUser3")),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_destination(self, uuid_mockup):
        """Test POST Subscription with a invalid Destination URI"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.app.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="INVALID",
                EventTypes=["Alert"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_get_subscription(self, uuid_mockup):
        """Test GET Subscription"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        self.app.post("/redfish/v1/EventService/EventSubscriptions/",
                      data=json.dumps(dict(
                          Destination="http://www.dnsname.com/Destination1",
                          EventTypes=["Alert", "StatusChange"])),
                      content_type='application/json')

        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/Subscription.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

        response = self.app.get(
            "/redfish/v1/EventService/EventSubscriptions/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36a")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(subscription_mockup, result)

    def test_get_invalid_subscription(self):
        """Test GET invalid Subscription"""

        response = self.app.get(
            "/redfish/v1/EventService/EventSubscriptions/INVALID")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)
