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
    def setUp(self, ov_mock):
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
    def test_get_computer_system_sh_not_found(self, mock_get_ov_client):
        """Tests ComputerSystem with ServerHardware Not Found"""

        client = mock_get_ov_client()
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        client.server_hardware.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sht_not_found(self, mock_get_ov_client):
        """Tests ComputerSystem with ServerHardwareTypes not found"""

        client = mock_get_ov_client()
        client.server_hardware.get.return_value = \
            {'serverHardwareTypeUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware-types not found',
        })
        client.server_hardware_types.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sh_exception(self, mock_get_ov_client):
        """Tests ComputerSystem with ServerHardware exception"""

        client = mock_get_ov_client()
        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })
        client.server_hardware.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_sht_exception(self, mock_get_ov_client):
        """Tests ComputerSystem with  ServerHardwareTypes exception"""

        client = mock_get_ov_client()
        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        client.server_hardware_types.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system_unexpected_error(self, mock_get_ov_client):
        """Tests ComputerSystem with an unexpected error"""

        client = mock_get_ov_client()
        client.server_hardware.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_computer_system(self, mock_get_ov_client):
        """Tests ComputerSystem with a known Server Hardware"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/ServerHardware.json'
        ) as f:
            sh_dict = json.load(f)

        # Loading ServerHardwareTypes mockup value
        with open(
            'oneview_redfish_toolkit/mockups/ServerHardwareTypes.json'
        ) as f:
            sht_dict = json.load(f)

        # Loading ComputerSystem mockup result
        with open(
            'oneview_redfish_toolkit/mockups/ComputerSystem.json'
        ) as f:
            computer_system_str = f.read()

        # Create mock response
        ov = mock_get_ov_client()
        ov.server_hardware.get.return_value = sh_dict
        ov.server_hardware_types.get.return_value = sht_dict

        # Get ComputerSystem
        response = self.app.get(
            "/redfish/v1/Systems/0303437-3034-4D32-3230-313133364752"
        )

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(computer_system_str, json_str)
