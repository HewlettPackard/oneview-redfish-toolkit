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
from oneview_redfish_toolkit.blueprints import chassis
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestChassis(BaseFlaskTest):
    """Tests for Chassis blueprint

        @Todo(ff) List performed tests
        Tests:
            - enclosures
            - blades
            - racks
                - against know value
                - rack not found
                - unexpected exception
    """

    @classmethod
    def setUpClass(self):
        super(TestChassis, self).setUpClass()

        self.app.register_blueprint(chassis.chassis)

        # Loading Enclosure mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Enclosure.json'
        ) as f:
            self.enclosure = json.load(f)

        # Loading EnclosureEnvironmentalConfig mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'EnclosureEnvironmentalConfig.json'
        ) as f:
            self.enclosure_environment_configuration_mockup = json.load(f)

        # Loading EnclosureChassis mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/EnclosureChassis.json'
        ) as f:
            self.enclosure_chassis_mockup = json.load(f)

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading BladeChassis mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/BladeChassis.json'
        ) as f:
            self.blade_chassis_mockup = json.load(f)

        # Loading Rack mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Rack.json'
        ) as f:
            self.rack = json.load(f)

        # Loading RackChassis mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/RackChassis.json'
        ) as f:
            self.rack_chassis_mockup = json.load(f)

    #############
    # Enclosure #
    #############
    @mock.patch.object(chassis, 'g')
    def test_get_enclosure_chassis(self, g):
        """"Tests EnclosureChassis with a known Enclosure"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        g.oneview_client.enclosures.get.return_value = self.enclosure
        g.oneview_client.enclosures.get_environmental_configuration.\
            return_value = self.enclosure_environment_configuration_mockup

        # Get EnclosureChassis
        response = self.client.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(self.enclosure_chassis_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", self.enclosure["eTag"]),
            response.headers["ETag"])

    @mock.patch.object(chassis, 'g')
    def test_get_enclosure_not_found(self, g):
        """Tests EnclosureChassis with Enclosure not found"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'enclosure not found',
        })

        g.oneview_client.enclosures.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_get_enclosure_env_config_not_found(self, g):
        """Tests EnclosureChassis with Enclosure env_config not found"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]

        g.oneview_client.enclosures.get.return_value = self.enclosure

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'environmental configuration not found',
        })
        g.oneview_client.enclosures.get_environmental_configuration.\
            side_effect = e

        response = self.client.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_enclosure_unexpected_error(self, g):
        """Tests EnclosureChassis with an unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        g.oneview_client.enclosures.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_enclosure_env_config_unexpected_error(self, g):
        """Tests EnclosureChassis env_config with an unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]

        g.oneview_client.enclosures.get.return_value = self.enclosure
        g.oneview_client.enclosures.get_environmental_configuration.\
            side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    #############
    # Blade     #
    #############
    @mock.patch.object(chassis, 'g')
    def test_get_blade_chassis(self, g):
        """"Tests BladeChassis with a known Server Hardware"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        # Get BladeChassis
        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(self.blade_chassis_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", self.server_hardware["eTag"]),
            response.headers["ETag"])

    @mock.patch.object(chassis, 'g')
    def test_get_server_hardware_not_found(self, g):
        """Tests BladeChassis with Server Hardware not found"""

        g.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.return_value =\
            {'serverHardwareUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server hardware not found',
        })

        g.oneview_client.server_hardware.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_server_hardware_unexpected_error(self, g):
        """Tests BladeChassis with an unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    ########
    # Rack #
    ########
    @mock.patch.object(chassis, 'g')
    def test_get_rack_chassis(self, g):
        """"Tests RackChassis with a known Rack"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        g.oneview_client.racks.get.return_value = self.rack

        # Get RackChassis
        response = self.client.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(self.rack_chassis_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", self.rack["eTag"]),
            response.headers["ETag"])

    @mock.patch.object(chassis, 'g')
    def test_get_rack_not_found(self, g):
        """Tests RackChassis with Racks not found"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        g.oneview_client.racks.get.return_value = {'rackeUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'rack not found',
        })

        g.oneview_client.racks.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_rack_unexpected_error(self, g):
        """Tests RackChassis with an unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        g.oneview_client.racks.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_change_power_state(self, g):
        """Tests changes a SH chassi type with valid reset options

            Valid Reset Values:
                - On
                - ForceOff
                - GracefulShutdown
                - GracefulRestart
                - ForceRestart
                - PushPowerButton
        """
        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        g.oneview_client.server_hardware.update_power_state.return_value = \
            {"status": "OK"}

        reset_types = ["On", "ForceOff", "GracefulShutdown",
                       "GracefulRestart", "ForceRestart", "PushPowerButton"]

        for reset_type in reset_types:
            response = self.client.post(
                "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
                "/Actions/Chassis.Reset",
                data=json.dumps(dict(ResetType=reset_type)),
                content_type='application/json')

            json_str = response.data.decode("utf-8")

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqual(json_str, '{"ResetType": "%s"}' % reset_type)

    @mock.patch.object(chassis, 'g')
    def test_change_power_state_invalid_value(self, g):
        """Tests changes a SH chassi type with invalid power value"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.post(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
            "/Actions/Chassis.Reset",
            data=json.dumps(dict(ResetType="INVALID_TYPE")),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_change_power_state_unexpected_error(self, g):
        """Tests changes a SH chassi type with OneView unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.post(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
            "/Actions/Chassis.Reset",
            data=json.dumps(dict(ResetType="On")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_change_power_state_oneview_exception(self, g):
        """Tests changes a SH chassi type with OneView unexpected error"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.side_effect = e

        response = self.client.post(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
            "/Actions/Chassis.Reset",
            data=json.dumps(dict(ResetType="On")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(chassis, 'g')
    def test_change_power_state_unable_reset(self, g):
        """Tests changes a SH chassi type with SH unable to reset"""

        e = HPOneViewException({
            'errorCode': 'INVALID_POWER_CONTROL_REQUEST_POWER_COLDBOOT_OFF',
            'message': 'Unable to cold boot because the server is '
                       'currently off.'
        })

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        g.oneview_client.server_hardware.update_power_state.side_effect = e

        response = self.client.post(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
            "/Actions/Chassis.Reset",
            data=json.dumps(dict(ResetType="ForceRestart")),
            content_type='application/json')

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    def test_change_power_state_invalid_key(self):
        """Tests a SH chassi type with JSON key different of ResetType"""

        response = self.client.post(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
            "/Actions/Chassis.Reset",
            data=json.dumps(dict(INVALID_KEY="On")),
            content_type='application/json')
        error_msg = "Invalid JSON key: {}".format("INVALID_KEY")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_msg, result["error"]["message"])
