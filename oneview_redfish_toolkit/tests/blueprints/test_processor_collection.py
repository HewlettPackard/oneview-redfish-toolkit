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
from oneview_redfish_toolkit.blueprints import processor_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestProcessorCollection(BaseFlaskTest):
    """Tests for Processor Collection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestProcessorCollection, self).setUpClass()

        self.app.register_blueprint(processor_collection.processor_collection)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ProcessorCollection.json'
        ) as f:
            self.expected_processor_collection = json.load(f)

    def test_get_processor_collection_server_hardware_not_found(self):
        self.oneview_client.server_hardware.get.side_effect = \
            HPOneViewException({"errorCode": "RESOURCE_NOT_FOUND"})

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752/Systems/1/Processors/")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_processor(self):
        self.oneview_client.server_hardware.get.return_value = \
            self.server_hardware

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/30303437-3034-4D32-3230-313133364752/Systems/1/Processors/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.expected_processor_collection, result)
