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

from flask import Flask
from flask_api import status
from hpOneView import HPOneViewException

from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit.blueprints import zone
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestZone(BaseTest):
    """Tests for Zone blueprint"""

    def setUp(self):
        """Tests preparation"""

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(zone.zone)

        @self.app.errorhandler(HPOneViewException)
        def internal_server_error(exception):
            return ResponseBuilder.error_by_hp_oneview_exception(exception)

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(zone, 'g')
    def test_get_zone(self, g_mock):
        """Tests Zone"""

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplate.json'
        ) as f:
            server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'AvailableTargetsForSPT.json'
        ) as f:
            available_targets = json.load(f)

        with open('oneview_redfish_toolkit/mockups/oneview/'
                  'Drives.json') as f:
            drives = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Zone.json'
        ) as f:
            zone_mockup = json.load(f)

        g_mock.oneview_client.server_profile_templates.get\
            .return_value = server_profile_template
        g_mock.oneview_client.server_profiles.get_available_targets\
            .return_value = available_targets
        g_mock.oneview_client.index_resources.get_all\
            .return_value = drives

        response = self.app.get(
            "/redfish/v1/CompositionService/ResourceZones/1f0ca9ef-7f81-45e3"
            "-9d64-341b46cf87e0")

        # Gets json from response
        expected_result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(zone_mockup, expected_result)

    @mock.patch.object(zone, 'g')
    def test_get_zone_not_found(self, g_mock):
        """Tests Zone when UUID was not found"""

        g_mock.oneview_client.server_profile_templates.get.side_effect = \
            HPOneViewException({
                'errorCode': 'RESOURCE_NOT_FOUND',
                'message': 'SPT not found'
            })

        response = self.app.get(
            "/redfish/v1/CompositionService/ResourceZones/1f0ca9ef-7f81-45e3"
            "-9d64-341b46cf87e0")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
