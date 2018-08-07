# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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
from oneview_redfish_toolkit.blueprints import ethernet_interface
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestEthernetInterface(BaseFlaskTest):
    """Tests for EthernetInterface blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestEthernetInterface, self).setUpClass()

        self.app.register_blueprint(
            ethernet_interface.ethernet_interface)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

    def test_get_ethernet_interface_when_it_has_only_one_vlan(self):
        """Tests request a valid EthernetInterface when it has one vlan"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'EthernetInterfaceWithOnlyOneVlan.json'
        ) as f:
            ethernet_interface_mockup = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'NetworkForEthernetInterface.json'
        ) as f:
            network = json.load(f)

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.index_resources.get.return_value = network

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "EthernetInterfaces/1"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(ethernet_interface_mockup, result)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])

        # if verifies the URI of connection from ServerProfile.json mockup
        self.oneview_client.index_resources.get.assert_called_with(
            "/rest/ethernet-networks/19638712-679d-4232-9743-c7cb6c7bf718")

    def test_get_ethernet_interface_when_it_has_only_a_list_of_vlan(self):
        """Tests request a valid EthernetInterface when it has a vlans list"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'NetworkSetForEthernetInterface.json'
        ) as f:
            network_set = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EthernetInterfaceWithListOfVlans.json'
        ) as f:
            ethernet_interface_mockup = json.load(f)

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile
        self.oneview_client.index_resources.get.return_value = network_set

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "EthernetInterfaces/2"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(ethernet_interface_mockup, result)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])

        # if verifies the URI of connection from ServerProfile.json mockup
        self.oneview_client.index_resources.get.assert_called_with(
            "/rest/network-sets/76f584da-1f9d-40b8-9b9d-5ccb09810142")

    def test_get_ethernet_interface_when_id_is_not_found(self):
        """Tests request a not found EthernetInterface"""

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "EthernetInterfaces/3"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.index_resources.get.assert_not_called()

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "EthernetInterfaces/abc"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_ethernet_interface_when_profile_not_found(self):
        """Tests request EthernetInterface when server profile not found"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND'
        })

        self.oneview_client.server_profiles.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/"
            "EthernetInterfaces/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.index_resources.get.assert_not_called()
