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
from flask_api import status
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit import util

# Module libs
from oneview_redfish_toolkit.blueprints.computer_system import computer_system


class TestComputerSystem(unittest.TestCase):
    """Tests for ComputerSystem blueprint

        Tests:
            - server hardware not found
            - server hardware types not found
            - oneview exception server hardware
            - oneview exception server hardware type
            - oneview unexpected exception
            - know computer system
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(computer_system)

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sh_not_found(self, get_oneview_client_mockup):
        """Tests ComputerSystem with ServerHardware Not Found"""

        oneview_client = get_oneview_client_mockup()
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        oneview_client.server_hardware.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sht_not_found(
            self,
            get_oneview_client_mockup):
        """Tests ComputerSystem with ServerHardwareTypes not found"""

        oneview_client = get_oneview_client_mockup()
        oneview_client.server_hardware.get.return_value = \
            {'serverHardwareTypeUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware-types not found',
        })
        oneview_client.server_hardware_types.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sh_exception(self, get_oneview_client_mockup):
        """Tests ComputerSystem with ServerHardware exception"""

        oneview_client = get_oneview_client_mockup()
        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })
        oneview_client.server_hardware.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sht_exception(
            self,
            get_oneview_client_mockup):
        """Tests ComputerSystem with  ServerHardwareTypes exception"""

        oneview_client = get_oneview_client_mockup()
        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        oneview_client.server_hardware_types.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_unexpected_error(
            self,
            get_oneview_client_mockup):
        """Tests ComputerSystem with an unexpected error"""

        oneview_client = get_oneview_client_mockup()
        oneview_client.server_hardware.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system(self, get_oneview_client_mockup):
        """Tests ComputerSystem with a known Server Hardware"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/ServerHardwareTypes.json'
        ) as f:
            server_hardware_types = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/ComputerSystem.json'
        ) as f:
            computer_system_mockup = f.read()

        # Create mock response
        oneview_client = get_oneview_client_mockup()
        oneview_client.server_hardware.get.return_value = server_hardware
        oneview_client.server_hardware_types.get.return_value = \
            server_hardware_types

        # Get ComputerSystem
        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(computer_system_mockup, json_str)
