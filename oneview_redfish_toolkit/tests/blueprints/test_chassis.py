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
from oneview_redfish_toolkit.blueprints import chassis


class TestChassis(unittest.TestCase):
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

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mock):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(chassis.chassis)

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
        response = self.app.get(
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

        response = self.app.get(
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

        response = self.app.get(
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

        response = self.app.get(
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

        response = self.app.get(
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
        response = self.app.get(
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

        response = self.app.get(
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

        response = self.app.get(
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
        response = self.app.get(
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

        response = self.app.get(
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

        response = self.app.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
