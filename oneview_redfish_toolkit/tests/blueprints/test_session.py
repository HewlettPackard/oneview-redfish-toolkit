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
from hpOneView import HPOneViewException


# Module libs
from oneview_redfish_toolkit.blueprints.session \
    import session as session_blueprint
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestSession(BaseFlaskTest):
    """Tests for Session blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestSession, self).setUpClass()

        self.app.register_blueprint(session_blueprint)

        @self.app.errorhandler(status.HTTP_401_UNAUTHORIZED)
        def unauthorized_error(error):
            """Creates a Unauthorized Error response"""
            return ResponseBuilder.error_401(error)

    @mock.patch.object(connection, 'OneViewClient')
    @mock.patch.object(config, 'get_authentication_mode')
    def test_post_session(self, get_authentication_mode,
                          oneview_client_mockup):
        """Tests post Session"""

        # Loading Session mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/Session.json'
        ) as f:
            expected_session_mockup = json.load(f)

        client_session.init_map_clients()
        get_authentication_mode.return_value = 'session'

        # Create mock response
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = "sessionId"

        # POST Session
        response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="administrator",
                Password="password")),
            content_type='application/json')

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_session_mockup, result)
        self.assertIn("/redfish/v1/SessionService/Sessions/1",
                      response.headers["Location"])
        self.assertEqual("sessionId", response.headers["X-Auth-Token"])
        oneview_client_mockup.assert_called_with(
            {
                'ip': config.get_oneview_multiple_ips()[0],
                'credentials': {
                    'userName': 'administrator',
                    'password': 'password'
                },
                'api_version': config.get_api_version()
            }
        )

    @mock.patch.object(connection, 'OneViewClient')
    @mock.patch.object(config, 'get_authentication_mode')
    def test_post_session_with_login_domain_data(self, get_authentication_mode,
                                                 oneview_client_mockup):
        """Tests post Session when UserName has login domain information"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionForLoginWithDomain.json'
        ) as f:
            expected_session_mockup = json.load(f)

        client_session.init_map_clients()
        get_authentication_mode.return_value = 'session'

        # Create mock response
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = "sessionId"

        # POST Session
        response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="LOCAL\\administrator",
                Password="password")),
            content_type='application/json')

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_session_mockup, result)
        self.assertIn("/redfish/v1/SessionService/Sessions/1",
                      response.headers["Location"])
        self.assertEqual("sessionId", response.headers["X-Auth-Token"])
        oneview_client_mockup.assert_called_with(
            {
                'ip': config.get_oneview_multiple_ips()[0],
                'credentials': {
                    'userName': 'administrator',
                    'password': 'password',
                    'authLoginDomain': 'LOCAL'
                },
                'api_version': config.get_api_version()
            }
        )

    @mock.patch.object(connection, 'OneViewClient')
    def test_post_session_invalid_key(self, oneview_client_mockup):
        """Tests post session with an invalid JSON key"""

        # Create mock response
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = "sessionId"

        # POST Session
        response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                InvalidKey="administrator",
                Password="password")),
            content_type='application/json')

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        with open(
                'oneview_redfish_toolkit/mockups/errors/'
                'InvalidCredentialsJsonKey.json'
        ) as f:
            invalid_json_key = json.load(f)

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(result, invalid_json_key)

    @mock.patch.object(connection, 'OneViewClient')
    def test_post_session_oneview_exception(self, oneview_client_mockup):
        """Tests post session with HPOneViewException"""

        oneview_client = oneview_client_mockup()

        e = HPOneViewException({
            'errorCode': 'HTTP_401_UNAUTHORIZED',
            'message': 'Invalid user information',
        })

        oneview_client.connection.get_session_id.side_effect = e

        # POST Session
        response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="administrator",
                Password="password")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_401_UNAUTHORIZED,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(connection, 'OneViewClient')
    def test_post_session_unexpected_error(self, oneview_client_mockup):
        """Tests post session with an unexpected error"""

        oneview_client = oneview_client_mockup()

        oneview_client.connection.get_session_id.side_effect = Exception()

        # POST Session
        response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="administrator",
                Password="password")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
