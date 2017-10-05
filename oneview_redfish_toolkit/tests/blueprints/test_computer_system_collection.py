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

import json
import unittest
from unittest import mock

from flask import Flask
from flask import Response
from flask_api import status
from oneview_redfish_toolkit import util

from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints.computer_system_collection \
    import computer_system_collection


class TestComputerSystemCollection(unittest.TestCase):
    """Tests for ComputerSystemCollection blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    @mock.patch.object(util, 'get_oneview_client')
    def setUp(self, oneview_client_mockup, get_oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(computer_system_collection)

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

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_collection_empty(
            self,
            get_oneview_client_mockup):
        """Tests ComputerSystemCollection with an empty list"""

        oneview_client = get_oneview_client_mockup()
        oneview_client.server_hardware.get_all.return_value = []

        with open(
                'oneview_redfish_toolkit/mockups_errors/'
                'ServerHardwareListNotFound.json'
        ) as f:
            server_hardware_list_not_found = f.read()

        response = self.app.get("/redfish/v1/Systems/")

        # Gets json from response
        json_str = response.data.decode("utf-8")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(server_hardware_list_not_found, json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_collection_fail(
            self,
            get_oneview_client_mockup):
        """Tests ComputerSystemCollection with an error"""

        oneview_client = get_oneview_client_mockup()
        oneview_client.server_hardware.get_all.side_effect = Exception()

        with open(
                'oneview_redfish_toolkit/mockups_errors/'
                'Error500.json'
        ) as f:
            error_500 = f.read()

        response = self.app.get("/redfish/v1/Systems/")

        # Gets json from response
        json_str = response.data.decode("utf-8")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_500, json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_collection(
            self,
            get_oneview_client_mockup):
        """Tests ComputerSystemCollection with a known Server Hardware list"""

        # Read mock values
        with open(
                'oneview_redfish_toolkit/mockups_oneview/ServerHardwares.json'
        ) as f:
            server_hardware_list = json.loads(f.read())

        with open(
                'oneview_redfish_toolkit/mockups_redfish/'
                'ComputerSystemCollection.json'
        ) as f:
            computer_system_collection_mockup = f.read()

        # Create mock response
        oneview_client = get_oneview_client_mockup()
        oneview_client.server_hardware.get_all.return_value = \
            server_hardware_list

        # Get ComputerSystemCollection
        response = self.app.get("/redfish/v1/Systems/")

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(computer_system_collection_mockup, json_str)
