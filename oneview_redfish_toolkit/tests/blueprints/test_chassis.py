# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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
from flask_api import status
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit import util

# Module libs
from oneview_redfish_toolkit.blueprints.chassis \
    import chassis


class TestChassis(unittest.TestCase):
    """Tests for Chassis blueprint

        Tests:
            - enclosures
            - blades
            - racks
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, ov_mock):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.ini')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(chassis)

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    #############
    # Enclosure #
    #############
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_enclosure_chassis(
            self, mock_get_ov_client):
        """"Tests EnclosureChassis with a known Enclosure"""

        # Loading ov_enclosure mockup value
        with open(
                'oneview_redfish_toolkit/mockups/OneViewEnclosureChassis.json'
        ) as f:
            ov_enclosure = json.load(f)

        # Loading env_config mockup value
        with open(
                'oneview_redfish_toolkit/mockups/'
                'EnclosureEnvironmentalConfig.json'
        ) as f:
            env_config = json.load(f)

        # Loading rf_enclosure mockup result
        with open(
                'oneview_redfish_toolkit/mockups/RedfishEnclosureChassis.json'
        ) as f:
            rf_enclosure = f.read()

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "enclosures"}]
        ov.enclosures.get.return_value = ov_enclosure
        ov.enclosures.get_environmental_configuration.return_value = env_config

        # Get EnclosureChassis
        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rf_enclosure, json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_enclosure_not_found(self, mock_get_ov_client):
        """Tests EnclosureChassis with Enclosure not found"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "enclosures"}]
        ov.enclosures.get.return_value = \
            {'enclosureUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'enclosure not found',
        })

        ov.enclosures.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_enclosure_env_config_not_found(self, mock_get_ov_client):
        """Tests EnclosureChassis with Enclosure env_config not found"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "enclosures"}]

        # Loading ov_enclosure mockup value
        with open(
                'oneview_redfish_toolkit/mockups/OneViewEnclosureChassis.json'
        ) as f:
            ov_enclosure = json.load(f)

        ov.enclosures.get.return_value = ov_enclosure
        ov.enclosures.get_environmental_configuration.return_value = \
            {'enclosureUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'environmental configuration not found',
        })

        ov.enclosures.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_enclosure_unexpected_error(self, mock_get_ov_client):
        """Tests EnclosureChassis with an unexpected error"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "enclosures"}]
        ov.enclosures.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_enclosure_env_config_unexpected_error(self, mock_get_ov_client):
        """Tests EnclosureChassis env_config with an unexpected error"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "enclosures"}]

        # Loading ov_enclosure mockup value
        with open(
                'oneview_redfish_toolkit/mockups/OneViewEnclosureChassis.json'
        ) as f:
            ov_enclosure = json.load(f)

        ov.enclosures.get.return_value = ov_enclosure
        ov.enclosures.get_environmental_configuration.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    ########
    # Rack #
    ########
