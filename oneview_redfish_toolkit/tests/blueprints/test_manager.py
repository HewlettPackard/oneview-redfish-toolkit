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
from oneview_redfish_toolkit.blueprints import manager


class TestManager(unittest.TestCase):
    """Tests for Managers blueprint

        Tests:
            - enclosures
                - know value
                - not found error
                - unexpected error
            - blades
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(manager.manager)

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
    # Enclosure #
    #############
    @mock.patch.object(manager, 'g')
    def test_get_enclosure_manager(
            self, g):
        """"Tests EnclosureManager with a known Enclosure"""

        # Loading Enclosure mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Enclosure.json'
        ) as f:
            ov_enclosure = json.load(f)

        # Loading EnclosureManager mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/EnclosureManager.json'
        ) as f:
            rf_enclosure_manager = json.load(f)

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        g.oneview_client.enclosures.get.return_value = ov_enclosure
        g.oneview_client. appliance_node_information.get_version.return_value = \
            {"softwareVersion": "3.00.07-0288219"}

        # Get EnclosureManager
        response = self.app.get(
            "/redfish/v1/Managers/0000000000A66101"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rf_enclosure_manager, result)
        self.assertEqual(
            "{}{}".format("W/", ov_enclosure["eTag"]),
            response.headers["ETag"])

    @mock.patch.object(manager, 'g')
    def test_get_enclosure_not_found(self, g):
        """Tests EnclosureManager with Enclosure not found"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        g.oneview_client.enclosures.get.return_value = \
            {'enclosureUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'enclosure not found',
        })

        g.oneview_client.enclosures.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Managers/0000000000A66101"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(manager, 'g')
    def test_enclosure_unexpected_error(self, g):
        """Tests EnclosureManager with an unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        g.oneview_client.enclosures.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Managers/0000000000A66101"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    #############
    # Blade     #
    #############
    @mock.patch.object(manager, 'g')
    def test_get_blade_manager(
            self, g):
        """"Tests BladeManager with a known Server Hardware"""

        # Loading ServerHardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading BladeManager mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/BladeManager.json'
        ) as f:
            blade_manager_mockup = json.load(f)

        g.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.return_value = server_hardware
        g.oneview_client. appliance_node_information.get_version.return_value = \
            {"softwareVersion": "3.00.07-0288219"}

        # Get BladeManager
        response = self.app.get(
            "/redfish/v1/Managers/30303437-3034-4D32-3230-313133364752"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(blade_manager_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", server_hardware["eTag"]),
            response.headers["ETag"])

    @mock.patch.object(manager, 'g')
    def test_get_server_hardware_not_found(self, g):
        """Tests BladeManager with Server Hardware not found"""

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
            "/redfish/v1/Managers/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(manager, 'g')
    def test_server_hardware_unexpected_error(self, g):
        """Tests BladeManager with an unexpected error"""

        g.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Managers/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
