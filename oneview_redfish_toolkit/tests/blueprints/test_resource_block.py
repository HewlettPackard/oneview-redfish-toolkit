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
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import resource_block
from oneview_redfish_toolkit.tests.blueprints.base_flask import BaseFlaskTest


class TestResourceBlock(BaseFlaskTest):
    """Tests for ResourceBlock blueprint"""

    @classmethod
    def setUpClass(self):
        """Tests preparation"""
        super(TestResourceBlock, self).setUpClass()

        self.app.register_blueprint(resource_block.resource_block)

    @mock.patch.object(resource_block, 'g')
    def test_get_resurce_block_not_found(self, g):
        error = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found'
        })
        g.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}
        ]
        g.oneview_client.server_hardware.get.side_effect = error

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(resource_block, 'g')
    def test_get_resource_block_internal_error(self, g):
        with open('oneview_redfish_toolkit/mockups/errors/Error500.json') as f:
            error_500 = json.load(f)

        g.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}
        ]
        g.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_500, result)

    @mock.patch.object(resource_block, 'g')
    def test_get_resource_block(self, g):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview'
            '/ServerProfileTemplates.json'
        ) as f:
            server_profile_templates = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish'
            '/ServerHardwareResourceBlock.json'
        ) as f:
            expected_resource_block = json.load(f)

        g.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}
        ]
        g.oneview_client.server_hardware.get.return_value = server_hardware
        g.oneview_client.server_profile_templates.get_all.return_value = \
            server_profile_templates

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752")

        result = json.loads(response.data.decode("utf-8"))

        self.maxDiff = None

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(expected_resource_block, result)
