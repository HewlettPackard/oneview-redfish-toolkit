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
from collections import OrderedDict
import copy
import json
from unittest import mock

# 3rd party libs
from flask_api import status

# Module libs
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.blueprints import manager
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestManager(BaseFlaskTest):
    """Tests for Managers blueprint

        Tests:
            - manager
                - know value
                - not found error
    """

    @classmethod
    def setUpClass(self):
        super(TestManager, self).setUpClass()

        self.app.register_blueprint(manager.manager)

        # Loading ApplianceNodeInfo mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceNodeInfo.json'
        ) as f:
            self.appliance_info = json.load(f)

        # Loading ApplianceState mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceState.json'
        ) as f:
            self.appliance_state = json.load(f)

        # Loading ApplianceHealthStatus mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceHealthStatus.json'
        ) as f:
            self.appliance_health_status = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'Manager.json'
        ) as f:
            self.manager_mockup = json.load(f)

        self.map_appliance = OrderedDict({
            "10.0.0.1": self.appliance_info["uuid"]
        })

    @mock.patch.object(client_session, 'get_oneview_client')
    @mock.patch.object(multiple_oneview, 'execute_query_ov_client')
    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_get_manager(self, get_map_appliances, execute_query_ov_client,
                         get_oneview_client):
        """"Tests get Manager"""

        get_map_appliances.return_value = self.map_appliance
        get_oneview_client.return_value = self.oneview_client
        execute_query_ov_client.side_effect = [
            self.appliance_info, self.appliance_state,
            self.appliance_health_status
        ]

        # Get Manager
        response = self.client.get(
            "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.manager_mockup, result)

    @mock.patch.object(client_session, 'get_oneview_client')
    @mock.patch.object(multiple_oneview, 'execute_query_ov_client')
    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_all_manager_states(self, get_map_appliances,
                                execute_query_ov_client,
                                get_oneview_client):
        """"Tests get Manager with all possible States"""

        appliance_state = copy.deepcopy(self.appliance_info)
        manager_mockup = copy.deepcopy(self.manager_mockup)

        for oneview_state, redfish_state in status_mapping.\
                APPLIANCE_STATE_TO_REDFISH_STATE.items():

            appliance_state["state"] = oneview_state
            manager_mockup["Status"]["State"] = redfish_state

            get_map_appliances.return_value = self.map_appliance
            get_oneview_client.return_value = self.oneview_client
            execute_query_ov_client.side_effect = [
                self.appliance_info, appliance_state,
                self.appliance_health_status
            ]

            # Get Manager
            response = self.client.get(
                "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
            )

            result = json.loads(response.data.decode("utf-8"))

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(manager_mockup, result)

    @mock.patch.object(client_session, 'get_oneview_client')
    @mock.patch.object(multiple_oneview, 'execute_query_ov_client')
    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_all_manager_health_status(self, get_map_appliances,
                                       execute_query_ov_client,
                                       get_oneview_client):
        """Tests get Manager with all possible Health Status"""

        appliance_health_status = \
            copy.deepcopy(self.appliance_health_status)
        manager_mockup = copy.deepcopy(self.manager_mockup)

        for oneview_health_status, redfish_health_status in \
                status_mapping.MANAGER_HEALTH_STATE.items():

            appliance_health_status["members"][0]["severity"] = \
                oneview_health_status
            manager_mockup["Status"]["Health"] = redfish_health_status

            get_map_appliances.return_value = self.map_appliance
            get_oneview_client.return_value = self.oneview_client
            execute_query_ov_client.side_effect = [
                self.appliance_info, self.appliance_state,
                appliance_health_status
            ]

            # Get Manager
            response = self.client.get(
                "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
            )

            result = json.loads(response.data.decode("utf-8"))

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(manager_mockup, result)

    @mock.patch.object(client_session, 'get_oneview_client')
    @mock.patch.object(multiple_oneview, 'execute_query_ov_client')
    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_manager_not_found(self, get_map_appliances,
                               execute_query_ov_client,
                               get_oneview_client):
        """Tests Manager with an unexpected error"""

        get_map_appliances.return_value = self.map_appliance
        get_oneview_client.return_value = self.oneview_client
        execute_query_ov_client.side_effect = [
            self.appliance_info, self.appliance_state,
            self.appliance_health_status
        ]

        response = self.client.get(
            "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9657"
        )

        self.assertEqual(
            status.HTTP_404_NOT_FOUND,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
