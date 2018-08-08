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
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import computer_system
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestComputerSystem(BaseFlaskTest):
    """Tests for ComputerSystem blueprint

        Tests:
            - server hardware not found
            - server hardware types not found
            - oneview exception server hardware
            - oneview exception server hardware type
            - oneview unexpected exception
            - know computer system
            - change power state with valid power value
            - change power state with invalid power value
            - change power state with unexpected exception
            - change power state with SH not found
            - change power state with SHT not found
    """

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

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_not_found(self, g):
        """Tests ComputerSystem with ServerProfileTemplates not found"""

        g.oneview_client.server_profiles.get.side_effect = \
            self.not_found_server_profile
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get \
            .assert_called_with("0303437-3034-4D32-3230-313133364752")
        g.oneview_client.server_profile_templates.get \
            .assert_called_with("0303437-3034-4D32-3230-313133364752")

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sh_not_found(
            self,
            g):
        """Tests ComputerSystem with Server Hardware not found"""

        g.oneview_client.server_profiles.get.return_value = {
            "category": "server-profiles",
            "serverHardwareUri": "notFoundUri"
        }
        g.oneview_client.server_hardware.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_called_with('notFoundUri')
        g.oneview_client.server_hardware_types.get.assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sht_not_found(
            self,
            g):
        """Tests ComputerSystem with ServerHardwareType not found"""

        g.oneview_client.server_profiles.get.return_value = {
            "category": "server-profiles",
            "serverHardwareUri": "validURI",
            "serverHardwareTypeUri": "notFoundURI"
        }
        g.oneview_client.server_hardware.get.return_value = {}
        g.oneview_client.server_hardware_types.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_hardware.get.assert_called_with("validURI")
        g.oneview_client.server_hardware_types.get\
            .assert_called_with("notFoundURI")

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sh_exception(self, g):
        """Tests ComputerSystem with ServerHardware exception"""

        g.oneview_client.server_profiles.get.return_value = {
            "category": "server-profiles",
            "serverHardwareUri": "someURI"
        }
        g.oneview_client.server_hardware.get.side_effect = self.internal_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sht_exception(
            self,
            g):
        """Tests ComputerSystem with ServerHardwareTypes exception"""

        g.oneview_client.server_profiles.get.return_value = \
            {
                'serverHardwareTypeUri': 'invalidUri',
                'serverHardwareUri': 'validUri',
                'category': 'server-profiles'
            }
        g.oneview_client.server_hardware.get.return_value = {}  # some object
        g.oneview_client.server_hardware_types.get.side_effect = \
            self.internal_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get \
            .assert_called_with("0303437-3034-4D32-3230-313133364752")

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_spt_exception(
            self,
            g):
        """Tests ComputerSystem with ServerProfileTemplates exception"""

        g.oneview_client.server_profiles.get.side_effect = self.not_found_error
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.internal_error

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_unexpected_error(
            self,
            g):
        """Tests ComputerSystem with an unexpected error"""

        g.oneview_client.server_profiles.get.side_effect = self.not_found_error
        g.oneview_client.server_profile_templates.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_server_profile(self, g):
        """Tests ComputerSystem with a known Server Profile"""

        server_profile = copy.deepcopy(self.server_profile)
        server_profile["localStorage"]["sasLogicalJBODs"].pop(0)

        # Create mock response
        g.oneview_client.server_profiles.get.return_value = server_profile
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        g.oneview_client.server_hardware_types.get.return_value = \
            self.server_hardware_types
        g.oneview_client.sas_logical_jbods.get_drives.return_value = \
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
        g.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        g.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )
        g.oneview_client.server_hardware_types.get.assert_called_with(
            "/rest/server-hardware-types/FE50A6FE-B1AC-4E42-8D40-B73CA8CC0CD2"
        )
        g.oneview_client.sas_logical_jbods.get_drives.assert_called_with(
            "/rest/sas-logical-jbods/9e83a03d-7a84-4f0d-a8d7-bd05a30c3175"
        )
        g.oneview_client.server_profile_templates.get \
            .assert_not_called()

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_spt(self, g):
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
        g.oneview_client.server_profiles.get.side_effect = self.not_found_error
        g.oneview_client.server_profile_templates.get.return_value = \
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
        g.oneview_client.server_profiles.get \
            .assert_called_with("1f0ca9ef-7f81-45e3-9d64-341b46cf87e0")
        g.oneview_client.server_profile_templates.get \
            .assert_called_with("1f0ca9ef-7f81-45e3-9d64-341b46cf87e0")

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state(self, g):
        """Tests change SH power state with valid power values

            Valid Power Values:
                - On
                - ForceOff
                - GracefulShutdown
                - GracefulRestart
                - ForceRestart
                - PushPowerButton
        """

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        g.oneview_client.server_hardware.update_power_state.return_value = \
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

        g.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        g.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )
        g.oneview_client.server_hardware.update_power_state \
            .assert_called_with({
                'powerControl': 'MomentaryPress',
                'powerState': 'Off'
            }, "30303437-3034-4D32-3230-313133364752")

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_invalid_value(self, g):
        """Tests change SH power state with invalid power value"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.post(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(ResetType="INVALID_TYPE")),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        g.oneview_client.server_hardware.get.assert_called_with(
            "/rest/server-hardware/30303437-3034-4D32-3230-313130304752"
        )

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_unexpected_error(self, g):
        """Tests change SH power state with OneView unexpected error"""

        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.post(
            "/redfish/v1/Systems/30303437-3034-4D32-3230-313133364752"
            "/Actions/ComputerSystem.Reset",
            data=json.dumps(dict(ResetType="On")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_sh_exception(self, g):
        """Tests change SH power state with SH exception"""

        g.oneview_client.server_hardware.get.side_effect = self.internal_error

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

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_unable_reset(self, g):
        """Tests change SH power state with SH unable to reset"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        g.oneview_client.server_hardware.update_power_state.side_effect = \
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
        g.oneview_client.server_profiles.get.assert_called_with(
            "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        )
        g.oneview_client.server_hardware.get.assert_called_with(
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

    @mock.patch.object(computer_system, 'g')
    def test_remove_computer_system(self, g):
        """Tests delete computer system"""

        g.oneview_client.server_profiles.delete.return_value = True

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_204_NO_CONTENT,
            response.status_code
        )

    @mock.patch.object(computer_system, 'g')
    def test_remove_computer_system_sp_not_found(
            self,
            g):
        """Tests remove ComputerSystem with ServerProfile not found"""

        g.oneview_client.server_profiles.delete.side_effect = \
            self.not_found_error

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_remove_computer_system_exception(
            self,
            g):
        """Tests remove ComputerSystem with ServerProfile exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-profile error',
        })
        g.oneview_client.server_profiles.delete.side_effect = e

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_remove_computer_system_not_deleted(
            self,
            g):
        """Tests remove ComputerSystem with ServerProfile not deleted"""

        g.oneview_client.server_profiles.delete.return_value = False

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_remove_computer_system_task_completed(
            self,
            g):
        """Tests remove ComputerSystem with task completed"""

        task = {'taskState': 'Completed'}

        g.oneview_client.server_profiles.delete.return_value = task

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_204_NO_CONTENT,
            response.status_code
        )

    @mock.patch.object(computer_system, 'g')
    def test_remove_computer_system_task_error(
            self,
            g):
        """Tests remove ComputerSystem with task completed"""

        task = {'taskState': 'Error'}

        g.oneview_client.server_profiles.delete.return_value = task

        response = self.client.delete(
            "/redfish/v1/Systems/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)
