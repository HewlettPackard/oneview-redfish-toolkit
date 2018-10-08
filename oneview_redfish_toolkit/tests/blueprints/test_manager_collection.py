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
from collections import OrderedDict
import json

# 3rd party libs
from flask_api import status
from unittest import mock

# Module libs
from oneview_redfish_toolkit.blueprints import manager_collection
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestManagerCollection(BaseFlaskTest):
    """Tests for ManagerCollection blueprint

        Tests:
            - oneview unexpected exception
            - know manager collection
    """

    @classmethod
    def setUpClass(self):
        super(TestManagerCollection, self).setUpClass()

        self.app.register_blueprint(
            manager_collection.manager_collection)

    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_get_manager_collection_unexpected_error(
            self, get_map_appliances):
        """Tests ManagerCollection with an error"""

        get_map_appliances.side_effect = \
            Exception("An exception has occurred")

        with open(
                'oneview_redfish_toolkit/mockups/errors/'
                'Error500.json'
        ) as f:
            error_500 = json.load(f)

        response = self.client.get("/redfish/v1/Managers/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_500, result)

    @mock.patch.object(multiple_oneview, 'get_map_appliances')
    def test_get_manager_collection(self, get_map_appliances):
        """Tests a valid ManagerCollection"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'ManagerCollection.json'
        ) as f:
            manager_collection_mockup = json.load(f)

        appliance_info_list = OrderedDict()
        appliance_info_list["10.0.0.1"] = \
            "b08eb206-a904-46cf-9172-dcdff2fa9639"
        appliance_info_list["10.0.0.2"] = \
            "c9ba5ca4-c1f8-48c7-9798-1e8b8897ef50"

        # Create mock response
        get_map_appliances.return_value = appliance_info_list

        # Get ManagerCollection
        response = self.client.get("/redfish/v1/Managers/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(manager_collection_mockup, result)
