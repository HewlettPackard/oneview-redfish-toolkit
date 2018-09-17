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

# 3rd party libs
from unittest import mock
from unittest.mock import call

from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import computer_system
from oneview_redfish_toolkit.services import computer_system_service
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
            self.server_hardware['serverProfileUri'] = None

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

        self.sh_id = "30303437-3034-4D32-3230-313133364752"
        self.spt_id = "1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
        self.drive1_id = "e11dd3e0-78cd-47e8-bacb-9813f4bb58a8"
        self.drive2_id = "53bd734f-19fe-42fe-a8ef-3f1a83b4e5c1"

        self.common_calls_to_assert_hardware = [
            call(self.sh_id),
            call(self.spt_id),
            call(self.drive1_id),
            call(self.drive2_id)
        ]

        self.common_calls_to_assert_spt = [
            call(self.sh_id),
            call(self.spt_id),
            call(self.drive1_id),
            call(self.drive2_id),
            call(self.spt_id)
        ]

        self.common_calls_to_assert_drives = [
            call('/rest/drives/' + self.sh_id),
            call('/rest/drives/' + self.spt_id),
            call('/rest/drives/' + self.drive1_id),
            call('/rest/drives/' + self.drive2_id)
        ]

    def run_common_mock_to_server_hardware(self):
        ov_client = self.oneview_client
        ov_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            self.server_hardware,  # for multiple oneview (power update status)
            self.server_hardware  # for multiple oneview (create profile)
        ]
        ov_client.server_hardware.update_power_state.return_value = None

    def run_common_mock_to_server_profile_template(self):
        self.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.server_profile_template,
            self.not_found_error,
            self.not_found_error,
            self.server_profile_template
        ]

    def run_common_mock_to_drives(self):
        self.oneview_client.index_resources.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.drives[0],
            self.drives[1]
        ]

    def assert_common_calls(self):
        self.oneview_client.server_hardware.get.assert_has_calls(
            self.common_calls_to_assert_hardware)
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            self.common_calls_to_assert_spt)
        self.oneview_client.index_resources.get.assert_has_calls(
            self.common_calls_to_assert_drives)

    @mock.patch.object(computer_system_service, 'time')
    def test_create_system(self, time_mock):
        """Tests create a redfish System with Network, Storage and Server"""

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileBuiltFromTemplateToCreateASystem.json'
        ) as f:
            expected_server_profile_built = json.load(f)

        task_without_resource_uri = {
            "associatedResource": {
                "resourceUri": None
            },
            "uri": "/rest/tasks/123456"
        }

        task_with_resource_uri = {
            "associatedResource": {
                "resourceUri": self.server_profile["uri"]
            },
            "uri": "/rest/tasks/123456"
        }

        self.run_common_mock_to_server_hardware()
        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        # The connection.post return for /rest/server-profiles is a tuple
        self.oneview_client.connection.post.return_value = \
            (task_without_resource_uri, None)

        # The task will be requested 3 times in this case,
        # simulating the checking of resource uri
        self.oneview_client.tasks.get.side_effect = [
            task_without_resource_uri,
            task_without_resource_uri,
            task_with_resource_uri
        ]

        response = self.client.post(
            "/redfish/v1/Systems",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "/redfish/v1/Systems/" + self.server_profile["uuid"],
            response.headers["Location"]
        )

        self.oneview_client.server_hardware.get.assert_has_calls(
            self.common_calls_to_assert_hardware)
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            self.common_calls_to_assert_spt)
        self.oneview_client.index_resources.get.assert_has_calls(
            self.common_calls_to_assert_drives)
        self.oneview_client.server_profiles.create.assert_not_called()

        self.oneview_client.server_hardware.update_power_state \
            .assert_called_with({
                'powerControl': 'PressAndHold', 'powerState': 'Off'
            }, self.server_hardware['uuid'])
        self.oneview_client.tasks.get.assert_called_with(
            task_without_resource_uri["uri"])
        self.oneview_client.connection.post.assert_called_once_with(
            '/rest/server-profiles', expected_server_profile_built
        )
        self.assertEqual(self.oneview_client.tasks.get.call_count, 3)
        time_mock.sleep.assert_called_with(3)

    def test_create_when_server_hardware_already_belongs_to_system(self,):
        """Tests create when server profile already applied to the server"""
        sh_with_profile_uri = copy.deepcopy(self.server_hardware)
        sh_with_profile_uri["serverProfileUri"] = "/server-profiles/uuid_1"

        self.oneview_client.server_hardware.get.side_effect = [
            sh_with_profile_uri,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            sh_with_profile_uri,
            sh_with_profile_uri
        ]

        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        response = self.client.post(
            "/redfish/v1/Systems",
            data=json.dumps(self.data_to_create_system),
            content_type="application/json")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Computer System Resource Block already belongs to a "
                      "Composed System with ID uuid_1", str(result))

        self.oneview_client.connection.post.assert_not_called()

    @mock.patch.object(computer_system_service, 'config')
    def test_create_when_power_off_on_compose_is_not_configured(self,
                                                                config_mock):
        """Tests create when power_off is blank, should below a normal flow"""

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileBuiltFromTemplateToCreateASystem.json'
        ) as f:
            expected_server_profile_built = json.load(f)

        self.run_common_mock_to_server_hardware()
        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        config_mock.get_composition_settings.return_value = {
            'PowerOffServerOnCompose': ''
        }

        task_with_resource_uri = {
            "associatedResource": {
                "resourceUri": self.server_profile["uri"]
            },
            "uri": "/rest/tasks/123456"
        }

        self.oneview_client.connection.post.return_value = \
            (task_with_resource_uri, None)

        response = self.client.post(
            "/redfish/v1/Systems",
            data=json.dumps(self.data_to_create_system),
            content_type="application/json")

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        self.oneview_client.server_hardware.update_power_state \
            .assert_not_called()
        self.oneview_client.connection.post.assert_called_once_with(
            '/rest/server-profiles', expected_server_profile_built
        )

    @mock.patch.object(computer_system_service, 'config')
    def test_create_when_power_off_on_compose_has_wrong_configuration(
            self, config_mock):
        """Tests create when power_off is blank, should below a normal flow"""

        self.run_common_mock_to_server_hardware()
        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        config_mock.get_composition_settings.return_value = {
            'PowerOffServerOnCompose': 'ForceOffff'
        }

        response = self.client.post(
            "/redfish/v1/Systems",
            data=json.dumps(self.data_to_create_system),
            content_type="application/json")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertIn('There is no mapping for ForceOffff on the OneView',
                      str(result))

        self.oneview_client.server_hardware.update_power_state \
            .assert_not_called()
        self.oneview_client.connection.post.assert_not_called()

    @mock.patch.object(computer_system_service, 'time')
    def test_create_system_without_description(self, time_mock):
        """Tests create a redfish System with Network, Storage and Server"""

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileBuiltFromTemplateToCreateASystem.json'
        ) as f:
            expected_server_profile_built = json.load(f)

        task_without_resource_uri = {
            "associatedResource": {
                "resourceUri": None
            },
            "uri": "/rest/tasks/123456"
        }

        task_with_resource_uri = {
            "associatedResource": {
                "resourceUri": self.server_profile["uri"]
            },
            "uri": "/rest/tasks/123456"
        }

        data_to_create_without_desc = copy.deepcopy(self.data_to_create_system)
        del expected_server_profile_built['description']
        data_to_create_without_desc['Description'] = ''

        self.run_common_mock_to_server_hardware()
        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        # The connection.post return for /rest/server-profiles is a tuple
        self.oneview_client.connection.post.return_value = \
            (task_without_resource_uri, None)

        # The task will be requested 3 times in this case,
        # simulating the checking of resource uri
        self.oneview_client.tasks.get.side_effect = [
            task_without_resource_uri,
            task_without_resource_uri,
            task_with_resource_uri
        ]

        response = self.client.post(
            "/redfish/v1/Systems",
            data=json.dumps(data_to_create_without_desc),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "/redfish/v1/Systems/" + self.server_profile["uuid"],
            response.headers["Location"]
        )

        self.oneview_client.server_hardware.get.assert_has_calls(
            self.common_calls_to_assert_hardware)
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            self.common_calls_to_assert_spt)
        self.oneview_client.index_resources.get.assert_has_calls(
            self.common_calls_to_assert_drives)
        self.oneview_client.server_profiles.create.assert_not_called()

        self.oneview_client.tasks.get.assert_called_with(
            task_without_resource_uri["uri"])
        self.oneview_client.connection.post.assert_called_once_with(
            '/rest/server-profiles', expected_server_profile_built
        )
        self.assertEqual(self.oneview_client.tasks.get.call_count, 3)
        time_mock.sleep.assert_called_with(3)

    def test_create_system_when_request_content_is_wrong(self):
        """Tests trying create a redfish System without Links"""

        data_to_send = {
            "Name": "Composed System Without Links"
        }

        response = self.client.post("/redfish/v1/Systems",
                                    data=json.dumps(data_to_send),
                                    content_type='application/json')

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_hardware.get.assert_not_called()
        self.oneview_client.server_profile_templates.get.assert_not_called()
        self.oneview_client.index_resources.get.assert_not_called()
        self.oneview_client.connection.post.assert_not_called()

    def test_create_system_when_request_content_has_not_compute(self):
        """Tests trying create a redfish System without Compute Resource"""

        self.oneview_client.server_hardware.get.side_effect = [
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
        self.oneview_client.server_hardware.get.assert_has_calls(
            self.common_calls_to_assert_hardware)
        self.oneview_client.server_profile_templates.get.assert_not_called()
        self.oneview_client.index_resources.get.assert_not_called()
        self.oneview_client.connection.post.assert_not_called()

    def test_create_system_when_request_content_has_not_network(self):
        """Tests trying create a redfish System without Network Resource"""

        self.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]

        self.oneview_client.server_profile_templates.get.side_effect = [
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
        self.oneview_client.server_hardware.get.assert_has_calls(
            self.common_calls_to_assert_hardware)
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ])
        self.oneview_client.index_resources.get.assert_not_called()
        self.oneview_client.connection.post.assert_not_called()

    def test_create_system_when_request_content_has_not_a_valid_network(
            self):
        """Tests trying create a redfish System with a invalid Network"""

        self.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]

        self.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            self.server_profile_template,
            self.not_found_error,
            self.not_found_error
        ]

        data_to_send = copy.copy(self.data_to_create_system)
        # wrong SPT id
        data_to_send["Id"] = "75871d70-789e-4cf9-8bc8-6f4d73193578"

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
        self.oneview_client.server_hardware.get.assert_has_calls(
            self.common_calls_to_assert_hardware)
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(self.spt_id),
                call(self.drive1_id),
                call(self.drive2_id)
            ])
        self.oneview_client.index_resources.get.assert_not_called()
        self.oneview_client.connection.post.assert_not_called()

    @mock.patch.object(computer_system_service, 'time')
    def test_create_system_when_request_content_has_not_storage(self, _):
        """Tests create a redfish System without Storage.

            This test should works well.

            This case is when we are creating a System without Storage
            Resource Blocks, but the Server Profile Template related has a
            local storage controller configured properly
        """

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'PostToComposeSystemWithoutStorage.json'
        ) as f:
            data_to_send = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileBuiltFromZoneWithoutStorageToCreateASystem.json'
        ) as f:
            expected_server_profile_built = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfileTemplates.json'
        ) as f:
            list_spt = json.load(f)
            spt = list_spt[1]  # without local storage controller configured
            spt_id = spt["uri"].split("/")[-1]

        task = {
            "associatedResource": {
                "resourceUri": self.server_profile["uri"]
            },
            "uri": "/rest/tasks/123456"
        }

        self.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.server_hardware,  # for multiple oneview (power update status)
            self.server_hardware
        ]
        self.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            spt,
            spt,
        ]
        self.oneview_client.index_resources.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
        ]
        self.oneview_client.connection.post.return_value = (task, None)

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(data_to_send),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "/redfish/v1/Systems/" + self.server_profile["uuid"],
            response.headers["Location"]
        )
        self.oneview_client.server_hardware.get.assert_has_calls(
            [
                call(self.sh_id),
                call(spt_id),
            ])
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            [
                call(self.sh_id),
                call(spt_id),
                call(spt_id)
            ])
        self.oneview_client.index_resources.get.assert_has_calls(
            [
                call('/rest/drives/' + self.sh_id),
                call('/rest/drives/' + spt_id),
            ])

        self.oneview_client.connection.post.assert_called_with(
            '/rest/server-profiles',
            expected_server_profile_built)

    @mock.patch.object(computer_system_service, 'time')
    def test_create_system_when_has_not_storage_and_controller(self, _):
        """Tests create a System without Storage but with Storage Controller.

            This test should works well.

            This case is when we are creating a System without Storage
            Resource Blocks and the Server Profile Template related has not a
            local storage controller configured properly
        """

        task = {
            "associatedResource": {
                "resourceUri": self.server_profile["uri"]
            },
            "uri": "/rest/tasks/123456"
        }

        self.oneview_client.server_hardware.get.side_effect = [
            self.server_hardware,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            self.server_hardware,  # for multiple oneview (power update status)
            self.server_hardware  # Get for multiple OneView support
        ]

        template_without_controller = copy.deepcopy(
            self.server_profile_template)
        template_without_controller["localStorage"]["controllers"] = []
        self.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            template_without_controller,
            self.not_found_error,
            self.not_found_error,
            template_without_controller
        ]
        self.oneview_client.index_resources.get.side_effect = [
            self.not_found_error,
            self.not_found_error,
            self.not_found_error,
            self.not_found_error
        ]
        self.oneview_client.connection.post.return_value = (task, None)

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
        self.assert_common_calls()

    def test_create_system_when_a_generic_exception_is_raised(self):
        """Tests create a redfish System when occurs a generic exception"""

        self.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR,
                         response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_hardware.get.assert_called_with(self.sh_id)
        self.oneview_client.server_profile_templates.get.assert_not_called()
        self.oneview_client.index_resources.get.assert_not_called()

    @mock.patch.object(computer_system_service, 'time')
    def test_create_system_when_a_task_error_is_raised(self, _):
        """Tests create a System when the Oneview raises a task error.

            This test should return a http 403 with a error message.
            Some problems are server hardware is powered On and the drive used
            belongs to another enclosure.
        """

        task = {
            "associatedResource": {
                "resourceUri": None
            },
            "uri": "/rest/tasks/123456",
            "taskErrors": [
                {"message": "The server hardware 123 is powered on"}
            ]
        }

        self.run_common_mock_to_server_hardware()
        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        self.oneview_client.connection.post.return_value = (task, object())

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("The server hardware 123 is powered on",
                      response.data.decode())

        self.assert_common_calls()

    @mock.patch.object(computer_system_service, 'time')
    def test_when_has_more_than_one_task_error(self, _):
        """Tests create a System when the Oneview raises two task errors.

            This test should return a http 403 with a error message.
            Some problems are server hardware is powered On and the drive used
            belongs to another enclosure.
        """

        task = {
            "associatedResource": {
                "resourceUri": None
            },
            "uri": "/rest/tasks/123456",
            "taskErrors": [
                {"message": "The server hardware 123 is powered on"},
                {"message": "The drive used belongs to another enclosure"}
            ]
        }

        self.run_common_mock_to_server_hardware()
        self.run_common_mock_to_server_profile_template()
        self.run_common_mock_to_drives()

        self.oneview_client.connection.post.return_value = (task, object())

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        expected_error_msg = "The server hardware 123 is powered on\\n" \
                             "The drive used belongs to another enclosure\\n"

        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(expected_error_msg, response.data.decode())

        self.assert_common_calls()

    def test_create_system_when_has_storage_but_not_valid_controller(self):
        """Tests when the Server Profile Template has not a valid storage controller.

            This test should return a http 403 with a error message.

            The case is: the server profile template associated with the
            request has not a valid local storage controller configured,
            but the request has storage resource blocks to compose the system
        """

        self.run_common_mock_to_server_hardware()

        template_without_controller = copy.deepcopy(
            self.server_profile_template)
        template_without_controller["localStorage"]["controllers"] = []
        self.oneview_client.server_profile_templates.get.side_effect = [
            self.not_found_error,
            template_without_controller,
            self.not_found_error,
            self.not_found_error,
            template_without_controller
        ]

        self.run_common_mock_to_drives()

        response = self.client.post(
            "/redfish/v1/Systems/",
            data=json.dumps(self.data_to_create_system),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("The Server Profile Template should have a valid "
                      "storage controller to use the Storage Resource "
                      "Blocks passed",
                      response.data.decode())

        self.assert_common_calls()
