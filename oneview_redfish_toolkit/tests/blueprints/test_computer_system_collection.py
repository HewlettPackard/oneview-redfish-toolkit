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
import json
from unittest import mock

from flask_api import status

from oneview_redfish_toolkit.blueprints import computer_system_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestComputerSystemCollection(BaseFlaskTest):
    """Tests for ComputerSystemCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestComputerSystemCollection, self).setUpClass()

        self.app.register_blueprint(
            computer_system_collection.computer_system_collection)

    @mock.patch.object(computer_system_collection, 'g')
    def test_get_computer_system_collection_empty(self, g):
        """Tests ComputerSystemCollection with an empty list"""

        g.oneview_client.server_hardware.get_all.return_value = []

        response = self.client.get("/redfish/v1/Systems/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ServerProfilesAppliedCollectionEmpty.json'
        ) as f:
            expected_result = json.load(f)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(expected_result, result)

    @mock.patch.object(computer_system_collection, 'g')
    def test_get_computer_system_collection_fail(self, g):
        """Tests ComputerSystemCollection with an error"""

        g.oneview_client.server_hardware.get_all.side_effect = Exception()

        with open(
                'oneview_redfish_toolkit/mockups/errors/'
                'Error500.json'
        ) as f:
            error_500 = json.load(f)

        response = self.client.get("/redfish/v1/Systems/")

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_500, result)

    @mock.patch.object(computer_system_collection, 'g')
    def test_get_computer_system_collection(self, g):
        """Tests ComputerSystemCollection with a known Server Hardware list"""

        # Read mock values
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerProfilesApplied.json'
        ) as f:
            server_hardware_list = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'ComputerSystemCollection.json'
        ) as f:
            computer_system_collection_mockup = json.load(f)

        # Create mock response
        g.oneview_client.server_hardware.get_all.return_value = \
            server_hardware_list

        # Get ComputerSystemCollection
        response = self.client.get("/redfish/v1/Systems/")

        # Gets json from response

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(computer_system_collection_mockup, result)
