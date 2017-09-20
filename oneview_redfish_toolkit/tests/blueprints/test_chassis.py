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
                - agains know value
                - rack not found
                - unexpected exception
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, ov_mock):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

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
                'oneview_redfish_toolkit/mockups/Enclosure.json'
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
                'oneview_redfish_toolkit/mockups/EnclosureChassis.json'
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
                'oneview_redfish_toolkit/mockups/Enclosure.json'
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
                'oneview_redfish_toolkit/mockups/Enclosure.json'
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

    #############
    # Blade     #
    #############
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_blade_chassis(
            self, mock_get_ov_client):
        """"Tests BladeChassis with a known Server Hardware"""

        # Loading ov_serverhardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/ServerHardware.json'
        ) as f:
            ov_serverhardware = json.load(f)

        # Loading rf_serverhardware mockup result
        with open(
                'oneview_redfish_toolkit/mockups/BladeChassis.json'
        ) as f:
            rf_blade = f.read()

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        ov.server_hardware.get.return_value = ov_serverhardware

        # Get BladeChassis
        response = self.app.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rf_blade, json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_server_hardware_not_found(self, mock_get_ov_client):
        """Tests BladeChassis with Server Hardware not found"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        ov.server_hardware.get.return_value =\
            {'serverHardwareUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server hardware not found',
        })

        ov.server_hardware.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_server_hardware_unexpected_error(self, mock_get_ov_client):
        """Tests BladeChassis with an unexpected error"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        ov.server_hardware.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Chassis/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    ########
    # Rack #
    ########
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_rack_chassis(
            self, mock_get_ov_client):
        """"Tests RackChassis with a known Rack"""

        # Loading ov_rack mockup value
        with open(
                'oneview_redfish_toolkit/mockups/Rack.json'
        ) as f:
            ov_rack = json.load(f)

        # Loading rf_rack mockup result
        with open(
                'oneview_redfish_toolkit/mockups/RedfishRack.json'
        ) as f:
            rf_rack = f.read()

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "racks"}]
        ov.racks.get.return_value = ov_rack

        # Get RackChassis
        response = self.app.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(json_str, rf_rack)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_rack_not_found(self, mock_get_ov_client):
        """Tests RackChassis with Racks not found"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "rack"}]
        ov.racks.get.return_value = {'rackeUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'rack not found',
        })

        ov.racks.get.side_effect = e

        response = self.app.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_rack_unexpected_error(self, mock_get_ov_client):
        """Tests RackChassis with an unexpected error"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = [{"category": "racks"}]
        ov.racks.get.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Chassis/2AB100LMNB"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
