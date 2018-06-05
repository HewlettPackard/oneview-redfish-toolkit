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
import unittest
from unittest import mock

# 3rd party libs
from flask import Flask
from flask import Response
from flask_api import status

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints import resource_block_collection
from oneview_redfish_toolkit import util


class TestResourceBlockCollection(unittest.TestCase):
    """Tests for ResourceBlockCollection blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(
            resource_block_collection.resource_block_collection)

        @self.app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        def internal_server_error(error):
            """General InternalServerError handler for the app"""

            redfish_error = RedfishError(
                "InternalError",
                "The request failed due to an internal service error.  "
                "The service is still operational.")
            redfish_error.add_extended_info("InternalError")
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype="application/json")

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(resource_block_collection, 'g')
    def test_get_resource_block_collection_fail(self, g_mock):
        """Tests ResourceBlockCollection with an error"""

        g_mock.oneview_client.server_hardware.get_all.side_effect = Exception()

        with open(
            'oneview_redfish_toolkit/mockups/errors/Error500.json'
        ) as f:
            error_500 = json.load(f)

        response = self.app.get(
            "/redfish/v1/CompositionService/ResourceBlocks/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_500, result)

    @mock.patch.object(resource_block_collection, 'g')
    def test_get_resource_block_collection(self, g_mock):
        """Tests ResourceBlockCollection"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwares.json'
        ) as f:
            server_hardware_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfileTemplates.json'
        ) as f:
            server_profile_template_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ResourceBlockCollection.json'
        ) as f:
            resource_block_collection_mockup = json.load(f)

        g_mock.oneview_client.server_hardware.get_all.return_value = \
            server_hardware_list

        g_mock.oneview_client.server_profile_templates.get_all.return_value = \
            server_profile_template_list

        # Get ResourceBlockCollection
        response = self.app.get(
            "/redfish/v1/CompositionService/ResourceBlocks/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(resource_block_collection_mockup, result)

    @mock.patch.object(resource_block_collection, 'g')
    def test_get_resource_block_collection_empty(self, g_mock):
        """Tests ResourceBlockCollection with an empty list"""

        g_mock.oneview_client.server_hardware.get_all.return_value = []
        g_mock.oneview_client.server_profile_template.get_all.return_value = []

        # Get ResourceBlockCollection
        response = self.app.get(
            "/redfish/v1/CompositionService/ResourceBlocks/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        expected_result = {
            "@odata.type": "#ResourceBlockCollection.ResourceBlockCollection",
            "Name": "Resource Block Collection",
            "Members@odata.count": 0,
            "Members": [],
            "@odata.context": "/redfish/v1/$metadata#ResourceBlockCollection.ResourceBlockCollection",
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks"
        }

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(expected_result, result)
