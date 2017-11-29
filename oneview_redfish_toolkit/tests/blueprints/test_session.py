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
from hpOneView import HPOneViewException


# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints import session as session_file
from oneview_redfish_toolkit.blueprints.session \
    import session as session_blueprint
from oneview_redfish_toolkit import util


class TestSession(unittest.TestCase):
    """Tests for Session blueprint"""

    @mock.patch.object(session_file, 'OneViewClient')
    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup, util_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(session_blueprint)

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

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(session_file, 'OneViewClient')
    def test_post_session(self, oneview_client_mockup):
        """Tests post Session"""

        # Loading Session mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/Session.json'
        ) as f:
            session_mockup = f.read()

        # Create mock response
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = "sessionId"

        # POST Session
        response = self.app.post("/redfish/v1/SessionService/Sessions",
                                 data=json.dumps(dict(
                                     UserName="administrator",
                                     Password="password")),
                                 content_type='application/json')

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(session_mockup, json_str)
        self.assertIn("/redfish/v1/SessionService/Sessions/1",
                      response.headers["Location"])
        self.assertEqual("sessionId", response.headers["X-Auth-Token"])

    @mock.patch.object(session_file, 'OneViewClient')
    def test_post_session_invalid_key(self, oneview_client_mockup):
        """Tests post session with an invalid JSON key"""

        # Create mock response
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = "sessionId"

        # POST Session
        response = self.app.post("/redfish/v1/SessionService/Sessions",
                                 data=json.dumps(dict(
                                     InvalidKey="administrator",
                                     Password="password")),
                                 content_type='application/json')

        # Gets json from response
        json_str = response.data.decode("utf-8")

        with open(
                'oneview_redfish_toolkit/mockups_errors/'
                'InvalidJsonKey.json'
        ) as f:
            invalid_json_key = f.read()

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(json_str, invalid_json_key)

    @mock.patch.object(session_file, 'OneViewClient')
    def test_post_session_oneview_exception(self, oneview_client_mockup):
        """Tests post session with HPOneViewException"""

        oneview_client = oneview_client_mockup()

        e = HPOneViewException({
            'errorCode': 'HTTP_400_BAD_REQUEST',
            'message': 'Invalid user information',
        })

        oneview_client.connection.get_session_id.side_effect = e

        # POST Session
        response = self.app.post("/redfish/v1/SessionService/Sessions",
                                 data=json.dumps(dict(
                                     UserName="administrator",
                                     Password="password")),
                                 content_type='application/json')

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(session_file, 'OneViewClient')
    def test_post_session_unexpected_error(self, oneview_client_mockup):
        """Tests post session with an unexpected error"""

        oneview_client = oneview_client_mockup()

        oneview_client.connection.get_session_id.side_effect = Exception()

        # POST Session
        response = self.app.post("/redfish/v1/SessionService/Sessions",
                                 data=json.dumps(dict(
                                     UserName="administrator",
                                     Password="password")),
                                 content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
