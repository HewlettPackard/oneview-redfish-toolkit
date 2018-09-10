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

# Python libs
import json
from unittest import mock

# 3rd party libs
from flask_api import status

# Module libs
from oneview_redfish_toolkit.blueprints import session_service
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


@mock.patch.object(config, 'auth_mode_is_session')
class TestSessionService(BaseFlaskTest):
    """Tests for SessionService blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestSessionService, self).setUpClass()

        self.app.register_blueprint(session_service.session_service)

    def test_get_session_service_when_is_enabled(self, auth_mode_is_session):
        """Tests get SessionService when is enabled"""
        auth_mode_is_session.return_value = True

        response = self.client.get("/redfish/v1/SessionService")

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/SessionService.json'
        ) as f:
            session_service_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(session_service_mockup, result)

    def test_get_session_service_when_is_disabled(self, auth_mode_is_session):
        """Tests get SessionService when is disabled"""
        auth_mode_is_session.return_value = False

        response = self.client.get("/redfish/v1/SessionService")

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'SessionServiceDisabled.json'
        ) as f:
            session_service_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(session_service_mockup, result)
