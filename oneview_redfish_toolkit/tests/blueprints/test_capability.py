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

import json
from unittest import mock

from flask_api import status
from hpOneView import HPOneViewException

from oneview_redfish_toolkit.blueprints import capability
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestCapability(BaseFlaskTest):
    """Tests for Capability blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestCapability, self).setUpClass()

        self.app.register_blueprint(capability.capability)

    @mock.patch.object(capability, 'g')
    def test_get_capability(self, g_mock):
        """Tests Zone"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplate.json'
        ) as f:
            server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Capability.json'
        ) as f:
            capability_mockup = json.load(f)

        g_mock.oneview_client.server_profile_templates.get\
            .return_value = server_profile_template

        response = self.client.get(
            "/redfish/v1/System/Capabilities/1f0ca9ef-7f81-45e3"
            "-9d64-341b46cf87e0")

        # Gets json from response
        expected_result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(capability_mockup, expected_result)

    @mock.patch.object(capability, 'g')
    def test_get_capability_not_found(self, g_mock):
        """Tests Zone when UUID was not found"""

        g_mock.oneview_client.server_profile_templates.get.side_effect = \
            HPOneViewException({
                'errorCode': 'RESOURCE_NOT_FOUND',
                'message': 'SPT not found'
            })

        response = self.client.get(
            "/redfish/v1/System/Capabilities/1f0ca9ef-7f81-45e3"
            "-9d64-341b46cf87e0")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
