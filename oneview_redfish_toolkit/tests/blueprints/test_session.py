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
import copy
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
from oneview_redfish_toolkit.blueprints.zone_collection import zone_collection
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


@mock.patch.object(client_session, 'uuid')
@mock.patch.object(connection, 'OneViewClient')
class TestSession(BaseFlaskTest):
    """Tests for Session blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestSession, self).setUpClass()

        self.app.register_blueprint(session_blueprint)
        self.app.register_blueprint(zone_collection)

        @self.app.errorhandler(status.HTTP_401_UNAUTHORIZED)
        def unauthorized_error(error):
            """Creates a Unauthorized Error response"""
            return ResponseBuilder.error_401(error)

        self.session_id = "e2807c0b-87d6-4304-a773-6ec33521fb1c"
        self.token_id = "abc"

        self.session_ids = [
            'e2807c0b-87d6-4304-a773-6ec33521fb1c',
            '709cf49b-f367-417e-af70-ede782e0fa3c',
            'cd825af3-05c5-44a1-85f7-84e6e2e9fcb3'
        ]

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionCollection.json'
        ) as f:
            self.session_collection = json.load(f)

    def _build_common_sessions(self, uuid_mock):
        uuid_mock.uuid4.side_effect = self.session_ids

        client_session.init_map_clients()
        client_session._set_new_client_by_token('abc', '10.0.0.1')
        client_session._set_new_client_by_token('def', '10.0.0.2')
        client_session._set_new_client_by_token('ghi', '10.0.0.3')

    def test_get_session_collection(self, _, uuid_mock):
        """Tests get Session Collection"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionCollection.json'
        ) as f:
            expected_session_collection = json.load(f)

        uuid_mock.uuid4.side_effect = self.session_ids

        client_session.init_map_clients()
        client_session._set_new_client_by_token('abc', '10.0.0.1')
        client_session._set_new_client_by_token('def', '10.0.0.2')
        client_session._set_new_client_by_token('ghi', '10.0.0.3')

        response = self.client.get(
            "/redfish/v1/SessionService/Sessions",
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_session_collection, result)

    def test_get_session_collection_when_is_empty(self, _, __):
        """Tests get Session Collection when active session list is empty"""
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionCollectionEmpty.json'
        ) as f:
            expected_session_collection = json.load(f)

        client_session.init_map_clients()

        response = self.client.get(
            "/redfish/v1/SessionService/Sessions",
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_session_collection, result)

    def test_get_session(self, _, uuid_mock):
        """Tests get a specific Session"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/Session.json'
        ) as f:
            expected_session = json.load(f)

        uuid_mock.uuid4.side_effect = self.session_ids

        client_session.init_map_clients()
        client_session._set_new_client_by_token('abc', '10.0.0.1')
        client_session._set_new_client_by_token('def', '10.0.0.2')

        response = self.client.get(
            "/redfish/v1/SessionService/Sessions/" + expected_session["Id"],
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_session, result)

    def test_get_session_when_is_not_cached(self, _, uuid_mock):
        """Tests get a specific Session when session id is not present"""

        uuid_mock.uuid4.return_value = '709cf49b-f367-417e-af70-ede782e0fa3c'

        client_session.init_map_clients()
        client_session._set_new_client_by_token('abc', '10.0.0.1')

        response = self.client.get(
            "/redfish/v1/SessionService/Sessions/"
            "e2807c0b-87d6-4304-a773-6ec33521fb1c",
            content_type='application/json')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(config, 'get_authentication_mode')
    def test_post_session(self,
                          get_authentication_mode,
                          oneview_client_mockup,
                          uuid_mock):
        """Tests post Session"""

        # Loading Session mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/Session.json'
        ) as f:
            expected_session_mockup = json.load(f)

        client_session.init_map_clients()
        multiple_oneview.init_map_appliances()
        get_authentication_mode.return_value = 'session'

        # Create mock response
        uuid_mock.uuid4.return_value = self.session_id
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = self.token_id

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
        self.assertIn("/redfish/v1/SessionService/Sessions/" + self.session_id,
                      response.headers["Location"])
        self.assertEqual(self.token_id, response.headers["X-Auth-Token"])
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

        # gets the session by id
        response_of_get = self.client.get(response.headers["Location"],
                                          content_type='application/json')

        result_of_get = json.loads(response_of_get.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response_of_get.status_code)
        self.assertEqual(self.session_id, result_of_get["Id"])

    def test_post_many_sessions(self, oneview_client_mockup, uuid_mock):
        """Tests post many Sessions and gets them"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionCollection.json'
        ) as f:
            expected_session_collection = json.load(f)

        client_session.init_map_clients()
        multiple_oneview.init_map_appliances()

        session_ids = self.session_ids
        uuid_mock.uuid4.side_effect = session_ids

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.side_effect = [
            'abc',
            'def',
            'ghi'
        ]

        self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="user_1",
                Password="password")),
            content_type='application/json')

        self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="user_2",
                Password="password")),
            content_type='application/json')

        self.client.post(
            "/redfish/v1/SessionService/Sessions",
            data=json.dumps(dict(
                UserName="user_3",
                Password="password")),
            content_type='application/json')

        response = self.client.get('/redfish/v1/SessionService/Sessions',
                                   content_type='application/json')
        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_session_collection, result)

    @mock.patch.object(config, 'get_authentication_mode')
    def test_post_session_with_login_domain_data(self,
                                                 get_authentication_mode,
                                                 oneview_client_mockup,
                                                 uuid_mock):
        """Tests post Session when UserName has login domain information"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionForLoginWithDomain.json'
        ) as f:
            expected_session_mockup = json.load(f)

        client_session.init_map_clients()
        multiple_oneview.init_map_appliances()
        get_authentication_mode.return_value = 'session'

        # Create mock response
        uuid_mock.uuid4.return_value = self.session_id
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = self.token_id

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
        self.assertIn("/redfish/v1/SessionService/Sessions/" + self.session_id,
                      response.headers["Location"])
        self.assertEqual(self.token_id, response.headers["X-Auth-Token"])
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

    def test_post_session_invalid_key(self, oneview_client_mockup, _):
        """Tests post session with an invalid JSON key"""

        # Create mock response
        oneview_client = oneview_client_mockup()
        oneview_client.connection.get_session_id.return_value = self.token_id

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

    def test_post_session_oneview_exception(self, oneview_client_mockup, _):
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

    def test_post_session_unexpected_error(self, oneview_client_mockup, _):
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

    @mock.patch.object(config, 'get_authentication_mode')
    def test_remove_token_when_authorization_token_fail(self,
                                                        get_auth_mode,
                                                        _,
                                                        uuid_mock):
        """Tests removing a session when Oneview raises authorization error"""

        err = HPOneViewException({
            'errorCode': 'AUTHORIZATION',
            'message': 'Invalid user information',
        })

        get_auth_mode.return_value = 'session'

        self.oneview_client.server_profile_templates.get_all.side_effect = err

        self._build_common_sessions(uuid_mock)

        # Raises the error
        response = self.client.get('/redfish/v1/CompositionService/'
                                   'ResourceZones',
                                   headers={'X-Auth-Token': 'abc'},
                                   content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('application/json', response.mimetype)
        self.assertIn('Invalid user information', str(result))

        # when gets the Active Session should have only 2 sessions
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'SessionCollection.json'
        ) as f:
            expected_session_collection = json.load(f)
            del expected_session_collection["Members"][0]
            expected_session_collection["Members@odata.count"] = 2

        resp_active_sess = self.client.get(
            "/redfish/v1/SessionService/Sessions",
            content_type='application/json')

        result_active_sess = json.loads(resp_active_sess.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, resp_active_sess.status_code)
        self.assertEqual("application/json", resp_active_sess.mimetype)
        self.assertEqualMockup(expected_session_collection, result_active_sess)

    def test_logout(self, _, uuid_mock):
        """Tests logout successfully"""

        self._build_common_sessions(uuid_mock)

        response = self.client.delete('/redfish/v1/SessionService/Sessions/' +
                                      self.session_ids[0],
                                      headers={'X-Auth-Token': 'abc'},
                                      content_type='application/json')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual('application/json', response.mimetype)

        # when gets the Active Session should have only 2 sessions
        expected_session_collection = copy.deepcopy(self.session_collection)
        del expected_session_collection["Members"][0]
        expected_session_collection["Members@odata.count"] = 2

        resp_active_sess = self.client.get(
            "/redfish/v1/SessionService/Sessions",
            content_type='application/json')

        result_active_sess = json.loads(resp_active_sess.data.decode("utf-8"))

        self.assertEqualMockup(expected_session_collection, result_active_sess)

    def test_logout_when_session_belongs_to_other_client(self, _, uuid_mock):
        """Tests logout when session belongs to other client, returns 404"""

        self._build_common_sessions(uuid_mock)

        response = self.client.delete('/redfish/v1/SessionService/Sessions/' +
                                      self.session_ids[0],
                                      headers={'X-Auth-Token': 'def'},
                                      content_type='application/json')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual('application/json', response.mimetype)

        resp_active_sess = self.client.get(
            "/redfish/v1/SessionService/Sessions",
            content_type='application/json')

        result_active_sess = json.loads(resp_active_sess.data.decode("utf-8"))

        # when gets the Active Session should have all sessions
        self.assertEqualMockup(self.session_collection, result_active_sess)

    def test_logout_when_session_is_invalid(self, _, uuid_mock):
        """Tests logout when session is invalid, returns 404"""

        self._build_common_sessions(uuid_mock)

        response = self.client.delete('/redfish/v1/SessionService/Sessions/' +
                                      '12345678',
                                      headers={'X-Auth-Token': 'abc'},
                                      content_type='application/json')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual('application/json', response.mimetype)

        resp_active_sess = self.client.get(
            "/redfish/v1/SessionService/Sessions",
            content_type='application/json')

        result_active_sess = json.loads(resp_active_sess.data.decode("utf-8"))

        # when gets the Active Session should have all sessions
        self.assertEqualMockup(self.session_collection, result_active_sess)
