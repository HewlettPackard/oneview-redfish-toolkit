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

# 3rd party libs
from flask_api import status

# Module libs
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.blueprints import manager
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestManager(BaseFlaskTest):
    """Tests for Managers blueprint

        Tests:
            - manager
                - know value
                - not found error
                - unexpected error
    """

    @classmethod
    def setUpClass(self):
        super(TestManager, self).setUpClass()

        self.app.register_blueprint(manager.manager)

        # Loading ApplianceNodeInfoList mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceNodeInfoList.json'
        ) as f:
            self.appliance_info_list = json.load(f)

        # Loading ApplianceStateList mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceStateList.json'
        ) as f:
            self.appliance_state_list = json.load(f)

        # Loading ApplianceHealthStatusList mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceHealthStatusList.json'
        ) as f:
            self.appliance_health_status_list = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'Manager.json'
        ) as f:
            self.manager_mockup = json.load(f)

    def test_get_manager(self):
        """"Tests get Manager"""

        self.oneview_client.appliance_node_information.get_version.return_value = \
            self.appliance_info_list
        self.oneview_client.connection.get.side_effect = \
            [self.appliance_state_list, self.appliance_health_status_list]

        # Get Manager
        response = self.client.get(
            "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.manager_mockup, result)

    def test_get_manager_states(self):
        """"Tests get Manager with all possible States"""

        appliance_state_list = copy.deepcopy(self.appliance_info_list)
        manager_mockup = copy.deepcopy(self.manager_mockup)

        for oneview_state, redfish_state in status_mapping.\
                APPLIANCE_STATE_TO_REDFISH_STATE.items():

            appliance_state_list[0]["state"] = oneview_state
            manager_mockup["Status"]["State"] = redfish_state

            self.oneview_client.appliance_node_information.get_version.return_value = \
                self.appliance_info_list
            self.oneview_client.connection.get.side_effect = \
                [appliance_state_list, self.appliance_health_status_list]

            # Get Manager
            response = self.client.get(
                "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
            )

            result = json.loads(response.data.decode("utf-8"))

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(manager_mockup, result)

    def test_all_manager_states(self):
        """"Tests get Manager with all possible States"""

        appliance_state_list = copy.deepcopy(self.appliance_info_list)
        manager_mockup = copy.deepcopy(self.manager_mockup)

        for oneview_state, redfish_state in status_mapping.\
                APPLIANCE_STATE_TO_REDFISH_STATE.items():

            appliance_state_list[0]["state"] = oneview_state
            manager_mockup["Status"]["State"] = redfish_state

            self.oneview_client.appliance_node_information.get_version.return_value = \
                self.appliance_info_list
            self.oneview_client.connection.get.side_effect = \
                [appliance_state_list, self.appliance_health_status_list]

            # Get Manager
            response = self.client.get(
                "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
            )

            result = json.loads(response.data.decode("utf-8"))

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(manager_mockup, result)

    def test_all_manager_health_status(self):
        """Tests get Manager with all possible Health Status"""

        appliance_health_status_list = \
            copy.deepcopy(self.appliance_health_status_list)
        manager_mockup = copy.deepcopy(self.manager_mockup)

        for oneview_health_status, redfish_health_status in \
                status_mapping.MANAGER_HEALTH_STATE.items():

            appliance_health_status_list[0]["members"][0]["severity"] = \
                oneview_health_status
            manager_mockup["Status"]["Health"] = redfish_health_status

            self.oneview_client.appliance_node_information.get_version.return_value = \
                self.appliance_info_list
            self.oneview_client.connection.get.side_effect = \
                [self.appliance_state_list, appliance_health_status_list]

            # Get Manager
            response = self.client.get(
                "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
            )

            result = json.loads(response.data.decode("utf-8"))

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(manager_mockup, result)

    def test_manager_unexpected_error(self):
        """Tests Manager with an unexpected error"""

        self.oneview_client.appliance_node_information.get_version.side_effect = \
            Exception()
        self.oneview_client.connection.get.side_effect = \
            [self.appliance_state_list, self.appliance_health_status_list]

        response = self.client.get(
            "/redfish/v1/Managers/b08eb206-a904-46cf-9172-dcdff2fa9639"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
