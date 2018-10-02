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
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import service_root
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestServiceRoot(BaseFlaskTest):
    """Tests from ServiceRoot blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestServiceRoot, self).setUpClass()

        self.app.register_blueprint(
            service_root.service_root, url_prefix='/redfish/v1/')

    @mock.patch.object(service_root, 'connection')
    def test_service_root_oneview_exception(self, connection):
        """Tests ServiceROOT with an exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'appliance error',
        })

        connection.request_oneview.side_effect = e

        response = self.client.get("/redfish/v1/")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )

        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(config, 'get_authentication_mode')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    @mock.patch.object(config, 'get_credentials')
    @mock.patch.object(connection, 'request_oneview')
    @mock.patch.object(client_session, 'get_oneview_client')
    def test_get_service_root_when_auth_mode_is_session(
            self,
            get_oneview_client,
            request_oneview,
            get_credentials,
            get_oneview_multiple_ips,
            get_authentication_mode):
        """Tests get ServiceRoot when authentication mode is session"""

        get_authentication_mode.return_value = 'session'
        request_oneview.return_value = \
            {'uuid': '00000000-0000-0000-0000-000000000000'}
        get_oneview_multiple_ips.return_value = ['10.0.0.1']
        get_credentials.return_value = {'userName': '',
                                        'password': ''}

        result = self.client.get("/redfish/v1/")

        result = json.loads(result.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ServiceRoot.json'
        ) as f:
            service_root_mockup = json.load(f)

        self.assertEqualMockup(service_root_mockup, result)
        get_credentials.assert_not_called()
        get_oneview_client.assert_not_called()

    @mock.patch.object(config, 'get_authentication_mode')
    @mock.patch.object(config, 'get_oneview_multiple_ips')
    @mock.patch.object(config, 'get_credentials')
    @mock.patch.object(connection, 'request_oneview')
    @mock.patch.object(client_session, 'get_oneview_client')
    def test_get_service_root_when_auth_mode_is_conf(self,
                                                     get_oneview_client,
                                                     request_oneview,
                                                     get_credentials,
                                                     get_oneview_multiple_ips,
                                                     get_authentication_mode):
        """Tests get ServiceRoot when authentication mode is conf"""

        get_authentication_mode.return_value = 'conf'
        request_oneview.return_value = \
            {'uuid': '00000000-0000-0000-0000-000000000000'}
        get_oneview_multiple_ips.return_value = ['10.0.0.1']
        get_credentials.return_value = {'userName': '',
                                        'password': ''}

        result = self.client.get("/redfish/v1/")

        result = json.loads(result.data.decode("utf-8"))

        with open(
                'oneview_redfish_toolkit/mockups/redfish/ServiceRoot.json'
        ) as f:
            service_root_mockup = json.load(f)
            service_root_mockup['Links']['Sessions'] = {}

        self.assertEqualMockup(service_root_mockup, result)
        get_credentials.assert_not_called()
        get_oneview_client.assert_not_called()
