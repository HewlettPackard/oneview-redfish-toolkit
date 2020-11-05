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
from hpOneView.resources.servers.server_profiles import ServerProfiles
from hpOneView.resources.servers.server_hardware import ServerHardware

# Module libs
from oneview_redfish_toolkit.blueprints import network_interface_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestNetworkInterfaceCollection(BaseFlaskTest):
    """Tests for NetworkInterfaceCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestNetworkInterfaceCollection, self).setUpClass()

        self.app.register_blueprint(
            network_interface_collection.network_interface_collection)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

    def test_get_network_interface_collection(self):
        """Tests NetworkInterfaceCollection"""

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkInterfaceCollection.json'
        ) as f:
            network_interface_collection_mockup = json.load(f)

        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        serverhw_obj = ServerHardware(
            self.oneview_client, self.server_hardware)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.server_hardware.get_by_uri.return_value = \
            serverhw_obj

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(network_interface_collection_mockup, result)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get_by_uri.assert_called_with(
            self.server_profile["serverHardwareUri"])

    def test_get_network_interface_collection_when_profile_not_found(
        self):
        """Tests when the searching a server profile returns not found"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        self.oneview_client.server_profiles.get_by_id.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get_by_uri.assert_not_called()

    def test_get_network_interface_collection_when_server_hardware_not_found(
            self):
        """Tests when the searching a server hardware returns not found"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        self.oneview_client.server_profiles.get_by_id.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get_by_uri.assert_not_called()

    def test_get_network_interface_collection_when_profile_raise_any_exception(
        self):
        """Tests when the searching a server profile raises any exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        self.oneview_client.server_profiles.get_by_id.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "NetworkInterfaces/"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware.get_by_uri.assert_not_called()
