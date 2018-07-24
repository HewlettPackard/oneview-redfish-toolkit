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
import copy
import json
from unittest import mock

# 3rd party libs
from unittest.mock import call

from flask_api import status
from hpOneView.exceptions import HPOneViewException
from hpOneView.exceptions import HPOneViewTaskError

# Module libs
from oneview_redfish_toolkit.blueprints import computer_system
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestCreateComputerSystem(BaseFlaskTest):
    """Tests for Create a ComputerSystem blueprint endpoint"""

    @classmethod
    def setUpClass(self):
        super(TestCreateComputerSystem, self).setUpClass()

        self.app.register_blueprint(computer_system.computer_system)

        self.not_found_error = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'resource not found',
        })

        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'PostToComposeSystem.json'
        ) as f:
            self.data_to_create_system = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileTemplate.json'
        ) as f:
            self.server_profile_template = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'Drives.json'
        ) as f:
            self.drives = json.load(f)

        self.sh_id = "30303437-3034-4D32-3230-313131324752"
        self.spt_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
        self.drive1_id = "e11dd3e0-78cd-47e8-bacb-9813f4bb58a8"
        self.drive2_id = "53bd734f-19fe-42fe-a8ef-3f1a83b4e5c1"

    @mock.patch.object(computer_system, 'g')
    def test_create_system(self, g):
        """Tests create a redfish System with Network, Storage and Server"""

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileBuiltFromTemplateToCreateASystem.json'
        ) as f:
            expected_server_profile_built = json.load(f)

        g.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]
        g.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.server_profile_template,
            self.not_found_error,
            self.not_found_error,
            self.server_profile_template
        ]
        g.oneview_client.index_resources.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.drives[0],
            self.drives[1]
        ]
        g.oneview_client.server_profiles.create.return_value = \
            self.server_profile

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "/redfish/v1/Systems/" + self.server_profile["uuid"],
            response.headers["Location"]
        )
        g.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id),
                call(self.spt_id)
            ]
        )
        g.oneview_client.index_resources.get.assert_has_calls(
            [
                call('/rest/drives/' + self.sh_id),
                call('/rest/drives/' + self.spt_id),
                call('/rest/drives/' + self.drive1_id),
                call('/rest/drives/' + self.drive2_id)
            ]
        )

        g.oneview_client.server_profiles.create.assert_called_with(
            expected_server_profile_built
        )

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_request_content_is_wrong(self, g):
        """Tests trying create a redfish System without Links"""

        data_to_send = {
            "Name": "Composed System Without Links"
        }

        response = self.client.post("/redfish/v1/Systems/",
                                    data=json.dumps(data_to_send),
                                    content_type='application/json')

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_not_called()
        g.oneview_client.server_profile_templates.get.assert_not_called()
        g.oneview_client.index_resources.get.assert_not_called()
        g.oneview_client.server_profiles.create.assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_request_content_did_not_have_compute(self, g):
        """Tests trying create a redfish System without Compute Resource"""

        g.oneview_client.server_hardware.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn(
            "Should have a Computer System Resource Block",
            response.data.decode()
        )
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.server_profile_templates.get.assert_not_called()
        g.oneview_client.index_resources.get.assert_not_called()
        g.oneview_client.server_profiles.create.assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_request_content_did_not_have_network(self, g):
        """Tests trying create a redfish System without Network Resource"""

        g.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]

        g.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn(
            "Should have a valid Network Resource Block",
            response.data.decode()
        )
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.index_resources.get.assert_not_called()
        g.oneview_client.server_profiles.create.assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_request_content_did_not_have_a_valid_network(
            self, g):
        """Tests trying create a redfish System with a invalid Network"""

        g.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]

        g.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.server_profile_template,
            self.not_found_error,
            self.not_found_error
        ]

        data_to_send = copy.copy(self.data_to_create_system)
        data_to_send["Id"] = "123456789"

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(data_to_send),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn(
            "Should have a valid Network Resource Block",
            response.data.decode()
        )
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.index_resources.get.assert_not_called()
        g.oneview_client.server_profiles.create.assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_request_content_did_not_have_storage(self, g):
        """Tests create a redfish System without Storage. Should works well"""

        g.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]
        g.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.server_profile_template,
            self.not_found_error,
            self.not_found_error,
            self.server_profile_template
        ]
        g.oneview_client.index_resources.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]
        g.oneview_client.server_profiles.create.return_value = \
            self.server_profile

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "/redfish/v1/Systems/" + self.server_profile["uuid"],
            response.headers["Location"]
        )
        g.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id),
                call(self.spt_id)
            ]
        )
        g.oneview_client.index_resources.get.assert_has_calls(
            [
                call('/rest/drives/' + self.sh_id),
                call('/rest/drives/' + self.spt_id),
                call('/rest/drives/' + self.drive1_id),
                call('/rest/drives/' + self.drive2_id)
            ]
        )

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_a_generic_exception_is_raised(self, g):
        """Tests create a redfish System when occurs a generic exception"""

        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR,
                         response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_called_with(self.sh_id)
        g.oneview_client.server_profile_templates.get.assert_not_called()
        g.oneview_client.index_resources.get.assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_create_system_when_a_task_error_is_raised(self, g):
        """Tests create a System when the Oneview raises a task error.

            This test should return a http 403 with a error message.
            Some problems are server hardware is powered On and the drive used
            belongs to another enclosure.
        """

        g.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]
        g.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.server_profile_template,
            self.not_found_error,
            self.not_found_error,
            self.server_profile_template
        ]
        g.oneview_client.index_resources.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.drives[0],
            self.drives[1]
        ]

        error = HPOneViewTaskError('The server hardware 123 is powered on',)

        g.oneview_client.server_profiles.create.side_effect = error

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(error.msg, response.data.decode())
        g.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ]
        )
        g.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id),
                call(self.spt_id)
            ]
        )
        g.oneview_client.index_resources.get.assert_has_calls(
            [
                call('/rest/drives/' + self.sh_id),
                call('/rest/drives/' + self.spt_id),
                call('/rest/drives/' + self.drive1_id),
                call('/rest/drives/' + self.drive2_id)
            ]
        )
