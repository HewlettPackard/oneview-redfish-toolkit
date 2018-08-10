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
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.blueprints import resource_block
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestResourceBlock(BaseFlaskTest):
    """Tests for ResourceBlock blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestResourceBlock, self).setUpClass()

        self.app.register_blueprint(resource_block.resource_block)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplate.json'
        ) as f:
            self.server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drive.json'
        ) as f:
            self.drive = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/DriveIndexTrees.json'
        ) as f:
            self.drive_index_tree = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplates.json'
        ) as f:
            self.server_profile_templates = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish'
                '/ServerHardwareResourceBlock.json'
        ) as f:
            self.expected_resource_block = json.load(f)

        self.resource_not_found = HPOneViewException({
            "errorCode": "RESOURCE_NOT_FOUND",
            "message": "Any resource not found message"
        })

    @mock.patch.object(resource_block, 'g')
    def test_get_resource_block_not_found(self, g):
        g.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        g.oneview_client.index_resources.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(resource_block, 'g')
    def test_get_storage_resource_block(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        g.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        g.oneview_client.index_resources.get.return_value = self.drive
        g.oneview_client.connection.get.return_value = self.drive_index_tree
        g.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        g.oneview_client.index_resources.get.assert_called_with(
            self.drive["uri"])
        g.oneview_client.connection.get.assert_called_with(
            "/rest/index/trees/rest/drives/"
            "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e?parentDepth=3")
        g.oneview_client.server_profile_templates.get_all.assert_called_with()

    @mock.patch.object(resource_block, 'g')
    def test_get_storage_resource_block_when_drive_is_composed(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        expected_resource_block["CompositionStatus"]["CompositionState"] \
            = "Composed"

        drive_composed = copy.copy(self.drive)
        drive_composed["attributes"]["available"] = "no"

        g.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        g.oneview_client.index_resources.get.return_value = drive_composed
        g.oneview_client.connection.get.return_value = self.drive_index_tree
        g.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        g.oneview_client.index_resources.get.assert_called_with(
            self.drive["uri"])
        g.oneview_client.connection.get.assert_called_with(
            "/rest/index/trees/rest/drives/"
            "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e?parentDepth=3")
        g.oneview_client.server_profile_templates.get_all.assert_called_with()

    @mock.patch.object(resource_block, 'g')
    def test_get_server_hardware_resource_block(self, g):

        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        g.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.expected_resource_block, result)

    @mock.patch.object(resource_block, 'g')
    def test_all_server_hardware_resouce_block_states(self, g):
        server_hardware = copy.deepcopy(self.server_hardware)
        expected_rb = copy.deepcopy(self.expected_resource_block)

        for oneview_state, redfish_state in status_mapping.\
                SERVER_HARDWARE_STATE_TO_REDFISH_STATE_MAPPING.items():

            server_hardware["state"] = oneview_state
            expected_rb["Status"]["State"] = redfish_state
            expected_rb["CompositionStatus"]["CompositionState"] = \
                status_mapping.COMPOSITION_STATE_MAPPING.get(
                    oneview_state, None)

            g.oneview_client.server_hardware.get.return_value = \
                server_hardware
            g.oneview_client.server_profile_templates.get_all.return_value = \
                self.server_profile_templates

            response = self.client.get(
                "/redfish/v1/CompositionService/ResourceBlocks"
                "/30303437-3034-4D32-3230-313133364752")

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_rb, result)

    @mock.patch.object(resource_block, 'g')
    def test_all_server_hardware_resouce_block_health(self, g):
        server_hardware = copy.deepcopy(self.server_hardware)
        expected_cs = copy.deepcopy(self.expected_resource_block)

        for oneview_status, redfish_status in \
                status_mapping.HEALTH_STATE_MAPPING.items():
            server_hardware["status"] = oneview_status
            expected_cs["Status"]["Health"] = redfish_status

            g.oneview_client.server_hardware.get.return_value = \
                server_hardware
            g.oneview_client.server_profile_templates.get_all.return_value = \
                self.server_profile_templates

            response = self.client.get(
                "/redfish/v1/CompositionService/ResourceBlocks"
                "/30303437-3034-4D32-3230-313133364752")

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_cs, result)

    @mock.patch.object(resource_block, 'g')
    def test_get_spt_resource_block(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ServerProfileTemplateResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        g.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

    @mock.patch.object(resource_block, 'g')
    def test_get_computer_system_not_found(self, g):
        g.oneview_client.server_hardware.get.side_effect = \
            HPOneViewException({"errorCode": "RESOURCE_NOT_FOUND"})

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752/Systems/1")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(resource_block, 'g')
    def test_get_computer_system(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ResourceBlockComputerSystem.json'
        ) as f:
            expected_computer_system = json.load(f)

        g.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752/Systems/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_computer_system, result)

    @mock.patch.object(resource_block, 'g')
    def test_get_ethernet_interface(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ResourceBlockEthernetInterface.json'
        ) as f:
            expected_ethernet_interface = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/EthernetNetwork.json'
        ) as f:
            ethernet_network = json.load(f)

        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template
        g.oneview_client.index_resources.get.return_value = \
            ethernet_network

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/EthernetInterfaces/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_ethernet_interface, result)

    @mock.patch.object(resource_block, 'g')
    def test_get_ethernet_interface_not_found(self, g):
        g.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/EthernetInterfaces/1")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(resource_block, 'g')
    def test_get_ethernet_interface_invalid_id(self, g):
        g.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/EthernetInterfaces/999")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
