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
import json
from unittest.mock import call

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import thermal
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestChassis(BaseFlaskTest):
    """Tests for Thermal blueprint

        Tests:
            - blades
            - enclosures
            - racks
    """

    @classmethod
    def setUpClass(self):
        super(TestChassis, self).setUpClass()

        self.app.register_blueprint(thermal.thermal)

    #############
    # Blade     #
    #############

    def test_get_blade_thermal(self):
        """"Tests BladeThermal with a known SH"""

        # Loading ServerHardwareUtilization mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareUtilization.json'
        ) as f:
            server_hardware_utilization = json.load(f)

        # Loading BladeChassisThermal mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'BladeChassisThermal.json'
        ) as f:
            blade_chassis_thermal_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        self.oneview_client.server_hardware.get_utilization.return_value = \
            server_hardware_utilization

        # Get BladeThermal
        response = self.client.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(blade_chassis_thermal_mockup, result)

    def test_get_blade_thermal_cached(self):
        """"Tests BladeThermal with a known SH"""

        # Loading ServerHardwareUtilization mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareUtilization.json'
        ) as f:
            server_hardware_utilization = json.load(f)

        # Loading BladeChassisThermal mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'BladeChassisThermal.json'
        ) as f:
            blade_chassis_thermal_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        self.oneview_client.server_hardware.get_utilization.return_value = \
            server_hardware_utilization

        uri = "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/"\
              "Thermal"
        uuid = "36343537-3338-4448-3538-4E5030333434"

        # Get BladeThermal
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(blade_chassis_thermal_mockup, result)

        # Get cached BladeThermal
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(blade_chassis_thermal_mockup, result)

        # Check for cached calls
        self.oneview_client.index_resources.get_all.assert_called_once_with(
            filter='uuid=' + uuid
        )
        assert self.oneview_client.server_hardware.get.has_calls(
            [call(uuid),
             call(uuid)]
        )
        self.assertTrue(category_resource.get_category_by_resource_id(uuid))

    def test_get_blade_not_found(self):
        """Tests BladeThermal with SH not found"""

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        self.oneview_client.server_hardware.get_utilization.return_value = \
            {'serverHardwareUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server hardware not found',
        })

        self.oneview_client.server_hardware.get_utilization.side_effect = e

        response = self.client.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_blade_unexpected_error(self):
        """Tests BladeThermal with an unexpected error"""

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        self.oneview_client.server_hardware.get_utilization.side_effect = \
            Exception()

        response = self.client.get(
            "/redfish/v1/Chassis/36343537-3338-4448-3538-4E5030333434/Thermal"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    #############
    # Enclosure #
    #############

    def test_get_encl_thermal(self):
        """"Tests EnclosureThermal with a known Enclosure"""

        # Loading EnclosureUtilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'EnclosureUtilization.json'
        ) as f:
            enclosure_utilization = json.load(f)

        # Loading EnclosureChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EnclosureChassisThermal.json'
        ) as f:
            enclosure_chasssis_thermal_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        self.oneview_client.enclosures.get_utilization.return_value = \
            enclosure_utilization

        # Get EnclosureThermal
        response = self.client.get(
            "/redfish/v1/Chassis/0000000000A66101/Thermal"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(enclosure_chasssis_thermal_mockup, result)

    def test_get_encl_thermal_cached(self):
        """"Tests EnclosureThermal with a known Enclosure"""

        # Loading EnclosureUtilization mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'EnclosureUtilization.json'
        ) as f:
            enclosure_utilization = json.load(f)

        # Loading EnclosureChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'EnclosureChassisThermal.json'
        ) as f:
            enclosure_chasssis_thermal_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        self.oneview_client.enclosures.get_utilization.return_value = \
            enclosure_utilization

        uri = "/redfish/v1/Chassis/0000000000A66101/Thermal"
        uuid = "0000000000A66101"

        # Get EnclosureThermal
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(enclosure_chasssis_thermal_mockup, result)

        # Get cached EnclosureThermal
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(enclosure_chasssis_thermal_mockup, result)

        # Check for cached calls
        self.oneview_client.index_resources.get_all.assert_called_once_with(
            filter='uuid=' + uuid
        )
        assert self.oneview_client.enclosures.get.has_calls(
            [call(uuid),
             call(uuid)]
        )
        self.assertTrue(category_resource.get_category_by_resource_id(uuid))

    ########
    # Rack #
    ########

    def test_get_rack_thermal(self):
        """"Tests RackThermal with a known Rack"""

        # Loading RackDeviceTopology mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'RackDeviceTopology.json'
        ) as f:
            rack_topology = json.load(f)

        # Loading RackChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/RackChassisThermal.json'
        ) as f:
            rack_chassis_thermal_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        self.oneview_client.\
            racks.get_device_topology.return_value = rack_topology

        # Get RackThermal
        response = self.client.get(
            "/redfish/v1/Chassis/2AB100LMNB/Thermal"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(rack_chassis_thermal_mockup, result)

    def test_get_rack_thermal_cached(self):
        """"Tests RackThermal with a known Rack"""

        # Loading RackDeviceTopology mockup value
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'RackDeviceTopology.json'
        ) as f:
            rack_topology = json.load(f)

        # Loading RackChassisThermal mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/RackChassisThermal.json'
        ) as f:
            rack_chassis_thermal_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "racks"}]
        self.oneview_client.\
            racks.get_device_topology.return_value = rack_topology

        uri = "/redfish/v1/Chassis/2AB100LMNB/Thermal"
        uuid = '2AB100LMNB'

        # Get RackThermal
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(rack_chassis_thermal_mockup, result)

        # Get cached RackThermal
        response = self.client.get(uri)

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(rack_chassis_thermal_mockup, result)

        # Check for cached calls
        self.oneview_client.index_resources.get_all.assert_called_once_with(
            filter='uuid=' + uuid
        )
        assert self.oneview_client.rackes.get.has_calls(
            [call(uuid),
             call(uuid)]
        )
        self.assertTrue(category_resource.get_category_by_resource_id(uuid))
