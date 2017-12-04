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
import unittest
from unittest import mock

# 3rd party libs
from flask import Flask
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit import util

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints.thermal import thermal


class TestChassis(unittest.TestCase):
    """Tests for Thermal blueprint

        Tests:
            - blades
            - enclosures
            - racks
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(thermal)

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

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    #############
    # Blade     #
    #############
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_blade_thermal(
            self, get_oneview_client_mockup):
        """"Tests BladeThermal with a known SH"""

        # Loading ServerHardwareUtilization mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareUtilization.json'
        ) as f:
            server_hardware_utilization = json.load(f)

        # Loading BladeChassisTermal mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'BladeChassisThermal.json'
        ) as f:
            blade_chassis_thermal_mockup = f.read()

        oneview_client = get_oneview_client_mockup()

        oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        oneview_client.server_hardware.get_utilization.return_value = \
            server_hardware_utilization

        # Get BladeThermal
        response = self.app.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(blade_chassis_thermal_mockup, json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_blade_not_found(self, get_oneview_client_mockup):
        """Tests BladeThermal with SH not found"""

        oneview_client = get_oneview_client_mockup()

        oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        oneview_client.server_hardware.get_utilization.return_value = \
            {'serverHardwareUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server hardware not found',
        })

        oneview_client.server_hardware.get_utilization.side_effect = e

        response = self.app.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_blade_unexpected_error(self, get_oneview_client_mockup):
        """Tests BladeThermal with an unexpected error"""

        oneview_client = get_oneview_client_mockup()

        oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        oneview_client.server_hardware.get_utilization.side_effect = \
            Exception()

        response = self.app.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    #############
    # Enclosure #
    #############
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_encl_thermal(self, get_oneview_client_mockup):
        """"Tests EnclosureThermal with a known Enclosure"""

        # Loading EnclosureUtilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'EnclosureUtilization.json'
        ) as f:
            enclosure_utilization = json.load(f)

        # Loading EnclosureChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EnclosureChassisThermal.json'
        ) as f:
            enclosure_chasssis_thermal_mockup = f.read()

        oneview_client = get_oneview_client_mockup()

        oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        oneview_client.enclosures.get_utilization.return_value = \
            enclosure_utilization

        # Get EnclosureThermal
        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101/Thermal"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(enclosure_chasssis_thermal_mockup, json_str)

    ########
    # Rack #
    ########
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_rack_thermal(self, get_oneview_client_mockup):
        """"Tests RackThermal with a known Rack"""

        # Loading RackDeviceTopology mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'RackDeviceTopology.json'
        ) as f:
            rack_topology = json.load(f)

        # Loading RackChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/RackChassisThermal.json'
        ) as f:
            rack_chassis_thermal_mockup = f.read()

        oneview_client = get_oneview_client_mockup()

        oneview_client.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        oneview_client.racks.get_device_topology.return_value = rack_topology

        # Get RackThermal
        response = self.app.get(
            "/redfish/v1/Chassis/2AB100LMNB/Thermal"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rack_chassis_thermal_mockup, json_str)
