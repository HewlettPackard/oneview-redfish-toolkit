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

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import network_interface
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestNetworkInterface(BaseFlaskTest):
    """Tests for NetworkInterface blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestNetworkInterface, self).setUpClass()

        self.app.register_blueprint(network_interface.network_interface)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        self.not_found_error = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'any message not found'
        })

    def test_get_network_interface(self):
        """Tests NetworkInterfaceCollection"""

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkInterface3.json'
        ) as f:
            network_interface_mockup = json.load(f)

        self.oneview_client.server_profiles.get.return_value = \
            self.server_profile

        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/3"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_interface_mockup, result)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get.assert_called_with(
            self.server_profile["serverHardwareUri"])

    def test_get_network_interface_invalid_id(self):
        """Tests NetworkInterfaceCollection"""

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/invalid_id"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_not_called()
        self.oneview_client.server_hardware.get.assert_not_called()

    def test_get_network_interface_server_profile_not_found(
            self):
        """Tests NetworkInterface server profile not found"""

        self.oneview_client.\
            server_profiles.get.side_effect = self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/3"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get.assert_not_called()

    def test_get_network_interface_sh_not_found(
        self):
        """Tests NetworkInterface server hardware not found"""

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.\
            server_hardware.get.side_effect = self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/3"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get.assert_called_with(
            self.server_profile["serverHardwareUri"])

    def test_get_network_interface_server_profile_exception(
        self):
        """Tests NetworkInterface unknown exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware error',
        })
        self.oneview_client.server_profiles.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/3"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get.assert_not_called()
