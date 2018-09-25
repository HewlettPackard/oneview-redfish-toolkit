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
from collections import OrderedDict
import copy
import json
from unittest import mock

# 3rd party libs
from unittest.mock import call

from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.blueprints import resource_block
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit import multiple_oneview
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
            'oneview_redfish_toolkit/mockups/oneview/'
            'DriveComposedIndexTrees.json'
        ) as f:
            self.drive_composed_index_tree = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplates.json'
        ) as f:
            self.server_profile_templates = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/LogicalEnclosures.json'
        ) as f:
            self.log_encl_list = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish'
                '/ServerHardwareResourceBlock.json'
        ) as f:
            self.expected_sh_resource_block = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview'
                '/DriveEnclosureList.json'
        ) as f:
            self.drive_enclosure_list = json.load(f)

        self.resource_not_found = HPOneViewException({
            "errorCode": "RESOURCE_NOT_FOUND",
            "message": "Any resource not found message"
        })

    def test_get_resource_block_not_found(self):
        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        self.oneview_client.index_resources.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_storage_resource_block(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        self.oneview_client.index_resources.get.return_value = self.drive
        self.oneview_client.connection.get.side_effect = [
            self.drive_index_tree,
        ]
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.\
            logical_enclosures.get_all.return_value = self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        self.oneview_client.index_resources.get.assert_called_with(
            self.drive["uri"])
        self.oneview_client.connection.get.assert_has_calls(
            [
                call("/rest/index/trees/rest/drives/"
                     "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e?parentDepth=3"),
            ])
        self.oneview_client.\
            server_profile_templates.get_all.assert_called_with()
        self.oneview_client.logical_enclosures.get_all.assert_called_with()
        self.oneview_client.drive_enclosures.get_all.assert_called_with()

    def test_get_storage_resource_block_cached(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        self.oneview_client.index_resources.get.return_value = self.drive
        self.oneview_client.connection.get.side_effect = [
            self.drive_index_tree, self.drive_index_tree,
        ]
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.\
            logical_enclosures.get_all.return_value = self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        uri = "/redfish/v1/CompositionService/ResourceBlocks/"\
              "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e"
        uuid = uri.split('/')[-1]

        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        # Get cached storage resource block
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        self.oneview_client.server_profile_templates.get_all.has_calls(
            [call(uri),
             call(uri)]
        )
        self.oneview_client.server_hardware.get.assert_called_once_with(uuid)
        self.oneview_client.index_resources.get.assert_has_calls(
            [call('/rest/drives/' + uuid),
             call('/rest/drives/' + uuid)]
        )
        self.assertTrue(category_resource.get_category_by_resource_id(
            ('/rest/drives/' + uuid)))

    def test_get_storage_resource_block_when_drive_is_composed(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'StorageResourceBlockComposed.json'
        ) as f:
            expected_resource_block = json.load(f)

        drive_composed = copy.copy(self.drive)
        drive_composed["attributes"]["available"] = "no"

        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found
        self.oneview_client.index_resources.get.return_value = drive_composed
        self.oneview_client.connection.get.side_effect = [
            self.drive_composed_index_tree,
        ]
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        self.oneview_client.index_resources.get.assert_called_with(
            self.drive["uri"])
        self.oneview_client.connection.get.assert_has_calls(
            [
                call("/rest/index/trees/rest/drives/"
                     "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e?parentDepth=3"),
            ])
        self.oneview_client.\
            server_profile_templates.get_all.assert_called_with()
        self.oneview_client.logical_enclosures.get_all.assert_called_with()
        self.oneview_client.drive_enclosures.get_all.assert_called_with()

    def test_get_server_hardware_resource_block(self):
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.expected_sh_resource_block, result)

    def test_all_server_hardware_resouce_block_states_with_sp(self):
        server_hardware = copy.deepcopy(self.server_hardware)
        expected_rb = copy.deepcopy(self.expected_sh_resource_block)
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        for oneview_state, redfish_state in status_mapping.\
                SERVER_HARDWARE_STATE_TO_REDFISH_STATE.items():

            server_hardware["state"] = oneview_state
            expected_rb["Status"]["State"] = redfish_state
            expected_composition_state = status_mapping.\
                COMPOSITION_STATE.get(oneview_state)

            if not expected_composition_state:
                expected_composition_state = \
                    status_mapping.COMPOSITION_STATE["ProfileApplied"]

            expected_rb["CompositionStatus"]["CompositionState"] = \
                expected_composition_state

            self.oneview_client.server_hardware.get.return_value = \
                server_hardware

            response = self.client.get(
                "/redfish/v1/CompositionService/ResourceBlocks"
                "/30303437-3034-4D32-3230-313133364752")

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_rb, result)

    def test_all_server_hardware_resouce_block_states_without_sp(self):
        server_hardware = copy.deepcopy(self.server_hardware)
        server_hardware["serverProfileUri"] = None
        expected_rb = copy.deepcopy(self.expected_sh_resource_block)
        expected_rb["Links"].pop("ComputerSystems")
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        for oneview_state, redfish_state in status_mapping.\
                SERVER_HARDWARE_STATE_TO_REDFISH_STATE.items():

            server_hardware["state"] = oneview_state
            expected_rb["Status"]["State"] = redfish_state

            expected_composition_state = status_mapping.\
                COMPOSITION_STATE.get(oneview_state)

            if not expected_composition_state:
                expected_composition_state = status_mapping.\
                    COMPOSITION_STATE["NoProfileApplied"]

            expected_rb["CompositionStatus"]["CompositionState"] = \
                expected_composition_state

            self.oneview_client.server_hardware.get.return_value = \
                server_hardware

            response = self.client.get(
                "/redfish/v1/CompositionService/ResourceBlocks"
                "/30303437-3034-4D32-3230-313133364752")

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_rb, result)

    def test_all_server_hardware_resouce_block_health(self):
        server_hardware = copy.deepcopy(self.server_hardware)
        expected_cs = copy.deepcopy(self.expected_sh_resource_block)

        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        for oneview_status, redfish_status in \
                status_mapping.HEALTH_STATE.items():
            server_hardware["status"] = oneview_status
            expected_cs["Status"]["Health"] = redfish_status

            self.oneview_client.server_hardware.get.return_value = \
                server_hardware

            response = self.client.get(
                "/redfish/v1/CompositionService/ResourceBlocks"
                "/30303437-3034-4D32-3230-313133364752")

            result = json.loads(response.data.decode("utf-8"))

            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqualMockup(expected_cs, result)

        self.oneview_client.server_hardware.get.assert_called_with(
            self.server_hardware["uuid"])

        encl_group_uri = self.server_hardware["serverGroupUri"]
        sh_type_uri = self.server_hardware["serverHardwareTypeUri"]
        self.oneview_client.\
            server_profile_templates.get_all.assert_called_with(
                filter=["enclosureGroupUri='" + encl_group_uri + "'",
                        "serverHardwareTypeUri='" + sh_type_uri + "'"]
                )
        self.oneview_client.logical_enclosures.get_all.assert_called_with()
        self.oneview_client.drive_enclosures.get_all.assert_called_with()

    def test_get_spt_resource_block(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ServerProfileTemplateResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        self.oneview_client.logical_enclosures.get_all.assert_called_with()
        self.oneview_client.drive_enclosures.get_all.assert_called_with()

    def test_get_spt_resource_block_cached(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ServerProfileTemplateResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        uri = "/redfish/v1/CompositionService/ResourceBlocks"\
              "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0"
        uuid = uri.split('/')[-1]

        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        # Get cached spt resource block
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        self.oneview_client.server_hardware.get.assert_called_once_with(uuid)
        self.oneview_client.server_profile_templates.get.assert_has_calls(
            [call(uuid),
             call(uuid)]
        )
        self.assertTrue(category_resource.get_category_by_resource_id(uuid))

    def test_get_spt_resource_when_template_has_not_valid_controller(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/SPTResourceBlockWithOnlyOneZone.json'
        ) as f:
            expected_resource_block = json.load(f)

        self.oneview_client.server_hardware.get.side_effect = \
            self.resource_not_found
        self.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_templates[1]
        self.oneview_client.logical_enclosures.get_all.return_value = \
            self.log_encl_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/75871d70-789e-4cf9-8bc8-6f4d73193578")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_resource_block, result)

        self.oneview_client.connection.get.assert_not_called()
        self.oneview_client.logical_enclosures.get.assert_not_called()

    def test_get_computer_system_not_found(self):
        self.oneview_client.server_hardware.get.side_effect = \
            HPOneViewException({"errorCode": "RESOURCE_NOT_FOUND"})

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752/Systems/1")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(multiple_oneview, 'get_map_resources')
    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_get_computer_system(self, get_map_appliances, get_map_resources):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ResourceBlockComputerSystem.json'
        ) as f:
            expected_computer_system = json.load(f)

        # Loading ApplianceNodeInfo mockup result
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ApplianceNodeInfo.json'
        ) as f:
            appliance_info = json.load(f)

        map_appliance = OrderedDict({
            "10.0.0.1": appliance_info["uuid"]
        })

        get_map_resources.return_value = OrderedDict({
            "30303437-3034-4D32-3230-313133364752": "10.0.0.1",
        })
        get_map_appliances.return_value = map_appliance
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752/Systems/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_computer_system, result)

    def test_get_ethernet_interface(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ResourceBlockEthernetInterface.json'
        ) as f:
            expected_ethernet_interface = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/EthernetNetwork.json'
        ) as f:
            ethernet_network = json.load(f)

        self.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template
        self.oneview_client.index_resources.get.return_value = \
            ethernet_network

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/EthernetInterfaces/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_ethernet_interface, result)

    def test_get_ethernet_interface_not_found(self):
        self.oneview_client.server_profile_templates.get.side_effect = \
            self.resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/EthernetInterfaces/1")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_ethernet_interface_invalid_id(self):
        self.oneview_client.server_profile_templates.get.return_value = \
            self.server_profile_template

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/1f0ca9ef-7f81-45e3-9d64-341b46cf87e0/EthernetInterfaces/999")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
