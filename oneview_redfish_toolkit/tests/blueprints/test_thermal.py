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
from oneview_redfish_toolkit.blueprints.thermal \
    import thermal


class TestChassis(unittest.TestCase):
    """Tests for Thermal blueprint

        Tests:
            - blades
            - enclosures
            - racks
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, ov_mock):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(thermal)

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    #############
    # Blade     #
    #############
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_blade_thermal(
            self, mock_get_ov_client):
        """"Tests BladeThermal with a known SH"""

        # Loading ov_sh_utilization mockup value
        with open(
                'oneview_redfish_toolkit/mockups/'
                'ServerHardwareUtilization.json'
        ) as f:
            ov_sh_utilization = json.load(f)

        # Loading rf_blade_thermal mockup result
        with open(
                'oneview_redfish_toolkit/mockups/BladeChassisThermal.json'
        ) as f:
            rf_blade_thermal = f.read()

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        ov.server_hardware.get_utilization.return_value = ov_sh_utilization

        # Get BladeThermal
        response = self.app.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rf_blade_thermal, json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_blade_not_found(self, mock_get_ov_client):
        """Tests BladeThermal with SH not found"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        ov.server_hardware.get_utilization.return_value = \
            {'serverHardwareUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server hardware not found',
        })

        ov.server_hardware.get_utilization.side_effect = e

        response = self.app.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_blade_unexpected_error(self, mock_get_ov_client):
        """Tests BladeThermal with an unexpected error"""

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        ov.server_hardware.get_utilization.side_effect = Exception()

        response = self.app.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    #############
    # Enclosure #
    #############
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_encl_thermal(self, mock_get_ov_client):
        """"Tests EnclosureThermal with a known Enclosure"""

        # Loading ov_encl_utilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/'
            'EnclosureUtilization.json'
        ) as f:
            ov_encl_utilization = json.load(f)

        # Loading rf_enclosure_thermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/EnclosureChassisThermal.json'
        ) as f:
            rf_enclosure_thermal = f.read()

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        ov.enclosures.get_utilization.return_value = ov_encl_utilization

        # Get EnclosureThermal
        response = self.app.get(
            "/redfish/v1/Chassis/0000000000A66101/Thermal"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rf_enclosure_thermal, json_str)

    ########
    # Rack #
    ########
    @mock.patch.object(util, 'get_oneview_client')
    def test_get_rack_thermal(self, mock_get_ov_client):
        """"Tests RackThermal with a known Rack"""

        # Loading ov_rack_utilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/'
            'RackDeviceTopology.json'
        ) as f:
            ov_rack_topo = json.load(f)

        # Loading rf_rack_thermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/RackChassisThermal.json'
        ) as f:
            rf_enclosure_thermal = f.read()

        ov = mock_get_ov_client()

        ov.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        ov.racks.get_device_topology.return_value = ov_rack_topo

        # Get RackThermal
        response = self.app.get(
            "/redfish/v1/Chassis/2AB100LMNB/Thermal"
        )

        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(rf_enclosure_thermal, json_str)
