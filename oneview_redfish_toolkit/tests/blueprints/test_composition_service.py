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

# Module libs
from oneview_redfish_toolkit.blueprints import composition_service
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestCompositionService(BaseFlaskTest):
    """Tests for CompositionService blueprint

        Tests:
            - composition service serialization exception
            - known composition service resource
    """

    @classmethod
    def setUpClass(self):
        super(TestCompositionService, self).setUpClass()

        self.app.register_blueprint(composition_service.composition_service)

    def test_get_composition_service(self):
        """Tests CompositionService"""

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'CompositionService.json'
        ) as f:
            composition_service_mockup = json.load(f)

        # Get CompositionService
        response = self.client.get("/redfish/v1/CompositionService/")

        # Gets json from response
        expected_result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(composition_service_mockup, expected_result)
