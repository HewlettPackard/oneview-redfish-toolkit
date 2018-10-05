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
from unittest import mock

# 3rd party libs
from unittest.mock import call

from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import resource_block
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit import single_oneview_context
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestSingleOneViewContext(BaseFlaskTest):
    """Tests for ResourceBlock blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestSingleOneViewContext, self).setUpClass()

        self.app.register_blueprint(resource_block.resource_block)

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
            'oneview_redfish_toolkit/mockups/oneview/LogicalEnclosures.json'
        ) as f:
            self.log_encl_list = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview'
                '/DriveEnclosureList.json'
        ) as f:
            self.drive_enclosure_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageResourceBlock.json'
        ) as f:
            self.expected_resource_block = json.load(f)

        self.resource_not_found = HPOneViewException({
            "errorCode": "RESOURCE_NOT_FOUND",
            "message": "Any resource not found message"
        })

    @mock.patch.object(config, 'get_oneview_multiple_ips')
    def test_get_storage_resource_block_single_ov(self,
                                                  get_oneview_multiple_ips):
        multiple_oneview.init_map_resources()
        category_resource.init_map_category_resources()

        list_ips = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
        get_oneview_multiple_ips.return_value = list_ips

        self.oneview_client.server_hardware.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.resource_not_found,
            ]
        self.oneview_client.server_profile_templates.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.resource_not_found,
            ]
        self.oneview_client.index_resources.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.drive,
            ]
        self.oneview_client.connection.get.return_value = self.drive_index_tree
        self.oneview_client.server_profile_templates.get_all.return_value = \
            self.server_profile_templates
        self.oneview_client.\
            logical_enclosures.get_all.return_value = self.log_encl_list
        self.oneview_client.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        uri = "/redfish/v1/CompositionService/ResourceBlocks"\
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e"
        uuid = uri.split('/')[-1]
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.expected_resource_block, result)

        self.oneview_client.server_hardware.get.assert_has_calls([
            call(uuid),
            call(uuid),
            call(uuid)
            ])
        self.oneview_client.server_profile_templates.get.assert_has_calls([
            call(uuid),
            call(uuid),
            call(uuid)
            ])
        self.oneview_client.index_resources.get.assert_has_calls([
            call(self.drive["uri"]),
            call(self.drive["uri"]),
            call(self.drive["uri"]),
            ])
        conn_uri = "/rest/index/trees/rest/drives/"\
            "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e?parentDepth=3"
        # Check for single calls on OneView context
        self.oneview_client.connection.get.assert_called_once_with(
            conn_uri)
        self.oneview_client.\
            server_profile_templates.get_all.assert_called_once_with()
        self.oneview_client.logical_enclosures.get_all.\
            assert_called_once_with()
        self.oneview_client.drive_enclosures.get_all.\
            assert_called_once_with()

        ov_ip_cached_drive = multiple_oneview.get_ov_ip_by_resource(
            self.drive['uri'])
        self.assertEqual(ov_ip_cached_drive, list_ips[2])

        ov_ip_cached_conn_drive = multiple_oneview.get_ov_ip_by_resource(
            conn_uri)
        self.assertTrue(ov_ip_cached_conn_drive, list_ips[2])

    @mock.patch.object(config, 'get_oneview_multiple_ips')
    @mock.patch.object(single_oneview_context, 'is_single_oneview_context')
    def test_get_storage_resource_block_without_single_ov(self,
                                                          is_single_ov_context,
                                                          get_ov_multiple_ips):
        multiple_oneview.init_map_resources()
        category_resource.init_map_category_resources()

        list_ips = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
        get_ov_multiple_ips.return_value = list_ips

        is_single_ov_context.return_value = False

        self.oneview_client.server_hardware.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.resource_not_found,
            ]
        self.oneview_client.server_profile_templates.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.resource_not_found,
            ]
        self.oneview_client.index_resources.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.drive,
            ]
        self.oneview_client.connection.get.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.drive_index_tree
            ]
        self.oneview_client.server_profile_templates.get_all.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.server_profile_templates
            ]
        self.oneview_client.logical_enclosures.get_all.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.log_encl_list
            ]
        self.oneview_client.drive_enclosures.get_all.side_effect = [
            self.resource_not_found,
            self.resource_not_found,
            self.drive_enclosure_list
            ]

        uri = "/redfish/v1/CompositionService/ResourceBlocks"\
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e"
        uuid = uri.split('/')[-1]
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.expected_resource_block, result)

        self.oneview_client.server_hardware.get.assert_has_calls([
            call(uuid),
            call(uuid),
            call(uuid)
            ])
        self.oneview_client.server_profile_templates.get.assert_has_calls([
            call(uuid),
            call(uuid),
            call(uuid)
            ])
        self.oneview_client.index_resources.get.assert_has_calls([
            call(self.drive["uri"]),
            call(self.drive["uri"]),
            call(self.drive["uri"]),
            ])
        conn_uri = "/rest/index/trees/rest/drives/"\
            "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e?parentDepth=3"
        # Check for multiple calls on multiple OneView context
        self.oneview_client.connection.get.assert_has_calls(
            [call(conn_uri), call(conn_uri), call(conn_uri)])
        self.oneview_client.server_profile_templates.get_all.has_calls(
            [call(), call(), call()])
        self.oneview_client.logical_enclosures.get_all.has_calls(
            [call(), call(), call()])
        self.oneview_client.drive_enclosures.get_all.has_calls(
            [call(), call(), call()])

        ov_ip_cached_drive = multiple_oneview.get_ov_ip_by_resource(
            self.drive['uri'])
        self.assertEqual(ov_ip_cached_drive, list_ips[2])

        ov_ip_cached_conn_drive = multiple_oneview.get_ov_ip_by_resource(
            conn_uri)
        self.assertTrue(ov_ip_cached_conn_drive, list_ips[2])
