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

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import manager
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestManager(BaseFlaskTest):
    """Tests for Managers blueprint

        Tests:
            - enclosures
                - know value
                - not found error
                - unexpected error
            - blades
    """

    @classmethod
    def setUpClass(self):
        super(TestManager, self).setUpClass()

        self.app.register_blueprint(manager.manager)

    #############
    # Enclosure #
    #############

    def test_get_enclosure_manager(
            self):
        """"Tests EnclosureManager with a known Enclosure"""

        # Loading Enclosure mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/Enclosure.json'
        ) as f:
            ov_enclosure = json.load(f)

        # Loading EnclosureManager mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/EnclosureManager.json'
        ) as f:
            rf_enclosure_manager = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        self.oneview_client.enclosures.get.return_value = ov_enclosure
        self.oneview_client. appliance_node_information.get_version.return_value = \
            {"softwareVersion": "3.00.07-0288219"}

        # Get EnclosureManager
        response = self.client.get(
            "/redfish/v1/Managers/0000000000A66101"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(rf_enclosure_manager, result)
        self.assertEqual(
            "{}{}".format("W/", ov_enclosure["eTag"]),
            response.headers["ETag"])

    def test_get_enclosure_not_found(self):
        """Tests EnclosureManager with Enclosure not found"""

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        self.oneview_client.enclosures.get.return_value = \
            {'enclosureUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'enclosure not found',
        })

        self.oneview_client.enclosures.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Managers/0000000000A66101"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_enclosure_unexpected_error(self):
        """Tests EnclosureManager with an unexpected error"""

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "enclosures"}]
        self.oneview_client.enclosures.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Managers/0000000000A66101"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    #############
    # Blade     #
    #############

    def test_get_blade_manager(
            self):
        """"Tests BladeManager with a known Server Hardware"""

        # Loading ServerHardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading BladeManager mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/BladeManager.json'
        ) as f:
            blade_manager_mockup = json.load(f)

        self.oneview_client.index_resources.get_all.return_value = \
            [{"category": "server-hardware"}]
        self.oneview_client.server_hardware.get.return_value = server_hardware
        self.oneview_client. appliance_node_information.get_version.return_value = \
            {"softwareVersion": "3.00.07-0288219"}

        # Get BladeManager
        response = self.client.get(
            "/redfish/v1/Managers/30303437-3034-4D32-3230-313133364752"
        )

        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(blade_manager_mockup, result)
        self.assertEqual(
            "{}{}".format("W/", server_hardware["eTag"]),
            response.headers["ETag"])

    def test_get_server_hardware_not_found(self):
        """Tests BladeManager with Server Hardware not found"""

        self.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        self.oneview_client.server_hardware.get.return_value =\
            {'serverHardwareUri': 'invalidUri'}
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server hardware not found',
        })

        self.oneview_client.server_hardware.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Managers/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_server_hardware_unexpected_error(self):
        """Tests BladeManager with an unexpected error"""

        self.oneview_client.index_resources.get_all.return_value = [
            {"category": "server-hardware"}]
        self.oneview_client.server_hardware.get.side_effect = Exception()

        response = self.client.get(
            "/redfish/v1/Managers/30303437-3034-4D32-3230-313133364752"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
