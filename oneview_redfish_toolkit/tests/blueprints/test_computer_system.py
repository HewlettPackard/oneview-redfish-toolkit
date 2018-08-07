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
from hpOneView.exceptions import HPOneViewException

# Module libs
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.blueprints import computer_system
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestComputerSystem(BaseFlaskTest):
    """Tests for ComputerSystem blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestComputerSystem, self).setUpClass()

        self.app.register_blueprint(computer_system.computer_system)

        self.internal_error = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'some internal error',
        })

        self.not_found_error = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'resource not found',
        })

        self.not_found_server_profile = HPOneViewException({
            'errorCode': 'ProfileNotFoundException',
            'message': 'The requested profile cannot be retrieved',
        })

        # Loading server_profile mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview'
                '/ServerHardwareTypes.json'
        ) as f:
            self.server_hardware_types = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/ComputerSystem.json'
        ) as f:
            self.computer_system_mockup = json.load(f)

        # Loading Drives mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Drives.json'
        ) as f:
            self.drives = json.load(f)

    def test_get_computer_system_not_found(self):
        """Tests ComputerSystem with ServerProfileTemplates not found"""

        self.oneview_client.server_profiles.get.side_effect = \
            self.not_found_server_profile
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get \
            .assert_called_with("0303437-3034-4D32-3230-313133364752")
        self.oneview_client.server_profile_templates.get \
            .assert_called_with("0303437-3034-4D32-3230-313133364752")

    def test_get_computer_system_sh_not_found(self):
        """Tests ComputerSystem with Server Hardware not found"""

        self.oneview_client.server_profiles.get.return_value = {
            "category": "server-profiles",
            "serverHardwareUri": "notFoundUri"
        }
        self.oneview_client.server_hardware.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_hardware.\
            get.assert_called_with('notFoundUri')
        self.oneview_client.server_hardware_types.get.assert_not_called()

    def test_get_computer_system_sht_not_found(self):
        """Tests ComputerSystem with ServerHardwareType not found"""

        self.oneview_client.server_profiles.get.return_value = {
            "category": "server-profiles",
            "serverHardwareUri": "validURI",
            "serverHardwareTypeUri": "notFoundURI"
        }
        self.oneview_client.server_hardware.get.return_value = {}
        self.oneview_client.server_hardware_types.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_hardware.get.assert_called_with("validURI")
        self.oneview_client.server_hardware_types.get\
            .assert_called_with("notFoundURI")

    def test_get_computer_system_sh_exception(self):
        """Tests ComputerSystem with ServerHardware exception"""

        self.oneview_client.server_profiles.get.return_value = {
            "category": "server-profiles",
            "serverHardwareUri": "someURI"
        }
        self.oneview_client.\
            server_hardware.get.side_effect = self.internal_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_get_computer_system_sht_exception(self):
        """Tests ComputerSystem with ServerHardwareTypes exception"""

        self.oneview_client.server_profiles.get.return_value = \
            {
                'serverHardwareTypeUri': 'invalidUri',
                'serverHardwareUri': 'validUri',
                'category': 'server-profiles'
            }
        self.oneview_client.\
            server_hardware.get.return_value = {}  # some object
        self.oneview_client.server_hardware_types.get.side_effect = \
            self.internal_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get \
            .assert_called_with("0303437-3034-4D32-3230-313133364752")

    def test_get_computer_system_spt_exception(self):
        """Tests ComputerSystem with ServerProfileTemplates exception"""

        self.oneview_client.\
            server_profiles.get.side_effect = self.not_found_error
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.internal_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_get_computer_system_unexpected_error(self):
        """Tests ComputerSystem with an unexpected error"""

        self.oneview_client.\
            server_profiles.get.side_effect = self.not_found_error
        self.oneview_client.\
            server_profile_templates.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_computer_system_server_profile(self):
        """Tests ComputerSystem with a known Server Profile"""

        server_profile = copy.deepcopy(self.server_profile)
        server_profile["localStorage"]["sasLogicalJBODs"].pop(0)

        # Create mock response
        self.oneview_client.server_profiles.get.return_value = server_profile
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        self.oneview_client.server_hardware_types.get.return_value = \
            self.server_hardware_types
        self.oneview_client.sas_logical_jbods.get_drives.return_value = \
            [self.drives[4]]

        # Get ComputerSystem
        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.computer_system_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", self.server_profile["eTag"]),
            response.headers["ETag"])
        self.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        self.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )
        self.oneview_client.server_hardware_types.get.assert_called_with(
            "/rest/server-hardware-types/FE50A6FE-B1AC-4E42-8D40-B73CA8CC0CD2"
        )
        self.oneview_client.sas_logical_jbods.get_drives.assert_called_with(
            "/rest/sas-logical-jbods/9e83a03d-7a84-4f0d-a8d7-bd05a30c3175"
        )
        self.oneview_client.server_profile_templates.get \
            .assert_not_called()

    def test_get_computer_system_spt(self):
        """Tests ComputerSystem with a known Server Profile Templates"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplate.json'
        ) as f:
            server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/CapabilitiesObject.json'
        ) as f:
            capabilities_obj_mockup = json.load(f)

        # Create mock response
        self.oneview_client.\
            server_profiles.get.side_effect = self.not_found_error
        self.oneview_client.server_profile_templates.get.return_value = \
            server_profile_template

        # Get ComputerSystem
        response = self.client.get(
            "/redfish/v1/Systems/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(capabilities_obj_mockup, result)
        self.oneview_client.server_profiles.get \
            .assert_called_with("1f0ca9ef-7f81-45e3-9d64-341b46cf87e0")
        self.oneview_client.server_profile_templates.get \
            .assert_called_with("1f0ca9ef-7f81-45e3-9d64-341b46cf87e0")

    def test_change_power_state(self):
        """Tests change SH power state with valid power values

            Valid Power Values:
                - On
                - ForceOff
                - GracefulShutdown
                - GracefulRestart
                - ForceRestart
                - PushPowerButton
        """

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        self.oneview_client.server_hardware.update_power_state.return_value = \
            {"status": "OK"}

        reset_types = ["On", "ForceOff", "GracefulShutdown",
                       "GracefulRestart", "ForceRestart", "PushPowerButton"]

        for reset_type in reset_types:
            response = self.client.post(
                "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
                "/Actions/ComputerSystem.Reset",
                data=json.dumps(dict(ResetType=reset_type)),
                content_type='application/json')

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)

            json_str = response.data.decode("utf-8")

            self.assertEqual(json_str, '{"ResetType": "%s"}' % reset_type)

        self.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        self.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )
        self.oneview_client.server_hardware.update_power_state \
            .assert_called_with({
                'powerControl': 'MomentaryPress',
                'powerState': 'Off'
            }, "30303437-3034-4D32-3230-313133364752")

    def test_change_power_state_invalid_value(self):
        """Tests change SH power state with invalid power value"""

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.post(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(ResetType="INVALID_TYPE")),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        self.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )

    def test_change_power_state_unexpected_error(self):
        """Tests change SH power state with OneView unexpected error"""

        self.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.post(
            "/redfish/v1/Systems/30303437-3034-4D32-3230-313133364752"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(ResetType="On")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_change_power_state_sh_exception(self):
        """Tests change SH power state with SH exception"""

        self.oneview_client.\
            server_hardware.get.side_effect = self.internal_error

        response = self.client.post(
            "/redfish/v1/Systems/30303437-3034-4D32-3230-313133364752"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(ResetType="On")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_change_power_state_unable_reset(self):
        """Tests change SH power state with SH unable to reset"""

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        self.oneview_client.server_hardware.update_power_state.side_effect = \
            self.internal_error

        response = self.client.post(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(ResetType="ForceRestart")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        self.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )

    def test_change_power_state_invalid_key(self):
        """Tests change SH power state with JSON key different of ResetType"""

        response = self.client.post(
            "/redfish/v1/Systems/30303437-3034-4D32-3230-313133364752"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(INVALID_KEY="On")),
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        with open(
                'oneview_redfish_toolkit/mockups/errors/'
                'InvalidJsonKey.json'
        ) as f:
            invalid_json_key = json.load(f)

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(result, invalid_json_key)

    def test_remove_computer_system(self):
        """Tests delete computer system"""

        self.oneview_client.server_profiles.delete.return_value = True

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_204_NO_CONTENT,
            response.status_code
        )

    def test_remove_computer_system_sp_not_found(self):
        """Tests remove ComputerSystem with ServerProfile not found"""

        self.oneview_client.server_profiles.delete.side_effect = \
            self.not_found_error

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_remove_computer_system_exception(self):
        """Tests remove ComputerSystem with ServerProfile exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-profile error',
        })
        self.oneview_client.server_profiles.delete.side_effect = e

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_remove_computer_system_not_deleted(self):
        """Tests remove ComputerSystem with ServerProfile not deleted"""

        self.oneview_client.server_profiles.delete.return_value = False

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_remove_computer_system_task_completed(self):
        """Tests remove ComputerSystem with task completed"""

        task = {'taskState': 'Completed'}

        self.oneview_client.server_profiles.delete.return_value = task

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_204_NO_CONTENT,
            response.status_code
        )

    def test_remove_computer_system_task_error(self):
        """Tests remove ComputerSystem with task completed"""

        task = {'taskState': 'Error'}

        self.oneview_client.server_profiles.delete.return_value = task

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_all_computer_system_health_status(self, g):
        server_hardware = copy.deepcopy(self.server_hardware)
        expected_cs = copy.deepcopy(self.computer_system_mockup)
        server_profile = copy.deepcopy(self.server_profile)
        server_profile["localStorage"]["sasLogicalJBODs"].pop(0)

        for oneview_status, redfish_status in \
                status_mapping.HEALTH_STATE_MAPPING.items():
            server_hardware["status"] = oneview_status
            expected_cs["Status"]["Health"] = redfish_status

            g.oneview_client.server_profiles.get.return_value = \
                server_profile
            g.oneview_client.server_hardware.get.return_value = \
                server_hardware
            g.oneview_client.server_hardware_types.get.return_value = \
                self.server_hardware_types
            g.oneview_client.sas_logical_jbods.get_drives.return_value = \
                [self.drives[4]]

            response = self.client.get(
                "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
            )

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_cs, result)

    @mock.patch.object(computer_system, 'g')
    def test_all_computer_system_states(self, g):
        expected_cs = copy.deepcopy(self.computer_system_mockup)
        server_profile = copy.deepcopy(self.server_profile)
        server_profile["localStorage"]["sasLogicalJBODs"].pop(0)

        for oneview_status, redfish_status in status_mapping.\
                SERVER_PROFILE_STATE_TO_REDFISH_STATE_MAPPING.items():

            server_profile["state"] = oneview_status
            expected_cs["Status"]["State"] = redfish_status

            g.oneview_client.server_profiles.get.return_value = \
                server_profile
            g.oneview_client.server_hardware.get.return_value = \
                self.server_hardware
            g.oneview_client.server_hardware_types.get.return_value = \
                self.server_hardware_types
            g.oneview_client.sas_logical_jbods.get_drives.return_value = \
                [self.drives[4]]

            response = self.client.get(
                "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
            )

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_cs, result)
