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
import copy
import json
from unittest import mock

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import vlan_network_interface
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestVLanNetworkInterface(BaseFlaskTest):
    """Tests for VLanNetworkInterface blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestVLanNetworkInterface, self).setUpClass()

        self.app.register_blueprint(
            vlan_network_interface.vlan_network_interface)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplateNetworkSet.json'
        ) as f:
            self.server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileNetworkSet.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/EthernetNetworkSet.json'
        ) as f:
            self.ethernet_network_mockup = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/NetworkSet.json'
        ) as f:
            self.network_set_mockup = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/VLanNetworkInterface.json'
        ) as f:
            self.expected_vlan_network_interface_spt = json.load(f)

        self.expected_vlan_network_interface_sp = \
            copy.deepcopy(self.expected_vlan_network_interface_spt)
        self.expected_vlan_network_interface_sp["@odata.id"] = \
            "/redfish/v1/Systems" \
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0" \
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718"

        self.resource_not_found = HPOneViewException({
            "errorCode": "RESOURCE_NOT_FOUND",
            "message": "Any resource not found message"
        })

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_network_interface(self, g):
        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        g.oneview_client.ethernet_networks.get.return_value = \
            self.ethernet_network_mockup

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(self.expected_vlan_network_interface_spt, result)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_called_with(
            self.expected_vlan_network_interface_spt["Id"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_network_interface_not_found(self, g):
        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        g.oneview_client.ethernet_networks.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_called_with(
            self.expected_vlan_network_interface_spt["Id"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_network_interface_spt_not_found(self, g):
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_not_called()

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_network_interface_connection_not_found(self, g):
        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        connection_id = "999"

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/" + connection_id +
            "/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_not_called()

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_network_interface_collection(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/VLanNetworkInterfaceCollectionSPT.json'
        ) as f:
            expected_vlan_network_interface_collection = json.load(f)

        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        g.oneview_client.network_sets.get.return_value = \
            self.network_set_mockup

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/"
            "EthernetInterfaces/1/VLANs")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(expected_vlan_network_interface_collection, result)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.network_sets.get.assert_called_with(
            self.network_set_mockup["uri"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_collection_not_found(self, g):
        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        g.oneview_client.network_sets.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.network_sets.get.assert_called_with(
            self.network_set_mockup["uri"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_spt_vlan_collection_with_spt_not_found(self, g):
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profile_templates.get.assert_called_with(
            self.server_profile_template["uri"].split("/")[-1])
        g.oneview_client.network_sets.get.assert_not_called()

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_network_interface(self, g):
        g.oneview_client.server_profiles.get.return_value = \
            self.server_profile

        g.oneview_client.ethernet_networks.get.return_value = \
            self.ethernet_network_mockup

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(self.expected_vlan_network_interface_sp, result)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_called_with(
            self.expected_vlan_network_interface_sp["Id"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_network_interface_not_found(self, g):
        g.oneview_client.server_profiles.get.return_value = \
            self.server_profile

        g.oneview_client.ethernet_networks.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_called_with(
            self.expected_vlan_network_interface_sp["Id"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_network_interface_sp_not_found(self, g):
        g.oneview_client.server_profiles.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_not_called()

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_network_interface_connection_not_found(self, g):
        g.oneview_client.server_profiles.get.return_value = \
            self.server_profile

        connection_id = "999"

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/" + connection_id +
            "/VLANs/19638712-679d-4232-9743-c7cb6c7bf718")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.ethernet_networks.get.assert_not_called()

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_network_interface_collection(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/VLanNetworkInterfaceCollectionSP.json'
        ) as f:
            expected_vlan_network_interface_collection = json.load(f)

        g.oneview_client.server_profiles.get.return_value = \
            self.server_profile

        g.oneview_client.network_sets.get.return_value = \
            self.network_set_mockup

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/"
            "EthernetInterfaces/1/VLANs")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(expected_vlan_network_interface_collection, result)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.network_sets.get.assert_called_with(
            self.network_set_mockup["uri"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_collection_not_found(self, g):
        g.oneview_client.server_profiles.get.return_value = \
            self.server_profile

        g.oneview_client.network_sets.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.network_sets.get.assert_called_with(
            self.network_set_mockup["uri"])

    @mock.patch.object(vlan_network_interface, 'g')
    def test_get_sp_vlan_collection_with_sp_not_found(self, g):
        g.oneview_client.server_profiles.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/Systems"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
            "/EthernetInterfaces/1/VLANs")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uri"].split("/")[-1])
        g.oneview_client.network_sets.get.assert_not_called()
