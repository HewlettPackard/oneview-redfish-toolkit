# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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
from flask import Flask
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints import computer_system
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestComputerSystem(BaseTest):
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

    def setUp(self):
        """Tests preparation"""

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(computer_system.computer_system)

        @self.app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        def internal_server_error(error):
            """General InternalServerError handler for the app"""

            redfish_error = RedfishError(
                "InternalError",
                "The request failed due to an internal service error.  "
                "The service is still operational.")
            redfish_error.add_extended_info("InternalError")
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype="application/json")

        @self.app.errorhandler(status.HTTP_404_NOT_FOUND)
        def not_found(error):
            """Creates a Not Found Error response"""
            redfish_error = RedfishError(
                "GeneralError", error.description)
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_404_NOT_FOUND,
                mimetype='application/json')

        @self.app.errorhandler(status.HTTP_501_NOT_IMPLEMENTED)
        def not_implemented(error):
            """Creates a Not Implemented Error response"""
            redfish_error = RedfishError(
                "ActionNotSupported", error.description)
            redfish_error.add_extended_info(
                message_id="ActionNotSupported",
                message_args=["action"])

            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_501_NOT_IMPLEMENTED,
                mimetype='application/json')

        @self.app.errorhandler(status.HTTP_400_BAD_REQUEST)
        def bad_request(error):
            """Creates a Bad Request Error response"""
            redfish_error = RedfishError(
                "PropertyValueNotInList", error.description)

            redfish_error.add_extended_info(
                message_id="PropertyValueNotInList",
                message_args=["VALUE", "PROPERTY"],
                related_properties=["PROPERTY"])

            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_400_BAD_REQUEST,
                mimetype='application/json')

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sh_not_found(self, g):
        """Tests ComputerSystem with ServerHardware Not Found"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        g.oneview_client.server_hardware.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sht_not_found(
            self,
            g):
        """Tests ComputerSystem with ServerHardwareTypes not found"""

        g.oneview_client.server_hardware.get.return_value = \
            {'serverHardwareTypeUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware-types not found',
        })
        g.oneview_client.server_hardware_types.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system_sh_exception(self, g):
        """Tests ComputerSystem with ServerHardware exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })
        g.oneview_client.server_hardware.get.side_effect = e

        response = self.app.get(
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
        """Tests ComputerSystem with  ServerHardwareTypes exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        g.oneview_client.server_hardware_types.get.side_effect = e

        response = self.app.get(
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

        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_get_computer_system(self, g):
        """Tests ComputerSystem with a known Server Hardware"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwareTypes.json'
        ) as f:
            server_hardware_types = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/ComputerSystem.json'
        ) as f:
            computer_system_mockup = json.load(f)

        # Create mock response
        g.oneview_client.server_hardware.get.return_value = server_hardware
        g.oneview_client.server_hardware_types.get.return_value = \
            server_hardware_types

        # Get ComputerSystem
        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(computer_system_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", server_hardware["eTag"]),
            response.headers["ETag"])

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

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            sh_dict = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareTypes.json'
        ) as f:
            sht_dict = json.load(f)

        g.oneview_client.server_hardware.get.return_value = sh_dict
        g.oneview_client.server_hardware_types.get.return_value = sht_dict
        g.oneview_client.server_hardware.update_power_state.return_value = \
            {"status": "OK"}

        reset_types = ["On", "ForceOff", "GracefulShutdown",
                       "GracefulRestart", "ForceRestart", "PushPowerButton"]

        for reset_type in reset_types:
            response = self.app.post("/redfish/v1/Systems/30303437-3034"
                                     "-4D32-3230-313133364752/Actions/"
                                     "ComputerSystem.Reset",
                                     data=json.dumps(
                                         dict(ResetType=reset_type)),
                                     content_type='application/json')

            # Tests response
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)

            json_str = response.data.decode("utf-8")

            self.assertEqual(json_str, '{"ResetType": "%s"}' % reset_type)

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_invalid_value(self, g):
        """Tests change SH power state with invalid power value"""

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            sh_dict = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareTypes.json'
        ) as f:
            sht_dict = json.load(f)

        g.oneview_client.server_hardware.get.return_value = sh_dict
        g.oneview_client.server_hardware_types.get.return_value = sht_dict

        response = self.app.post("/redfish/v1/Systems/30303437-3034-4D32-3230"
                                 "-313133364752/Actions/ComputerSystem.Reset",
                                 data=json.dumps(dict(
                                     ResetType="INVALID_TYPE")),
                                 content_type='application/json')

        # Tests response
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_unexpected_error(self, g):
        """Tests change SH power state with OneView unexpected error"""

        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.app.post("/redfish/v1/Systems/30303437-3034-4D32-3230"
                                 "-313133364752/Actions/ComputerSystem.Reset",
                                 data=json.dumps(dict(ResetType="On")),
                                 content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_sh_exception(self, g):
        """Tests change SH power state with SH exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })

        g.oneview_client.server_hardware.get.side_effect = e

        response = self.app.post("/redfish/v1/Systems/30303437-3034-4D32-3230"
                                 "-313133364752/Actions/ComputerSystem.Reset",
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
        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            sh_dict = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareTypes.json'
        ) as f:
            sht_dict = json.load(f)

        e = HPOneViewException({
            'errorCode': 'INVALID_POWER_CONTROL_REQUEST_POWER_COLDBOOT_OFF',
            'message': 'Unable to cold boot because the server is '
                       'currently off.'
        })

        g.oneview_client.server_hardware.get.return_value = sh_dict
        g.oneview_client.server_hardware_types.get.return_value = sht_dict
        g.oneview_client.server_hardware.update_power_state.side_effect = e

        response = self.app.post("/redfish/v1/Systems/30303437-3034-4D32-3230"
                                 "-313133364752/Actions/ComputerSystem.Reset",
                                 data=json.dumps(
                                     dict(ResetType="ForceRestart")),
                                 content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(computer_system, 'g')
    def test_change_power_state_sht_exception(self, g):
        """Tests change SH power state with SHT exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })

        g.oneview_client.server_hardware_types.get.side_effect = e

        response = self.app.post("/redfish/v1/Systems/30303437-3034-4D32-3230"
                                 "-313133364752/Actions/ComputerSystem.Reset",
                                 data=json.dumps(dict(ResetType="On")),
                                 content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_change_power_state_invalid_key(self):
        """Tests change SH power state with JSON key different of ResetType"""

        response = self.app.post("/redfish/v1/Systems/30303437-3034-4D32-3230"
                                 "-313133364752/Actions/ComputerSystem.Reset",
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
