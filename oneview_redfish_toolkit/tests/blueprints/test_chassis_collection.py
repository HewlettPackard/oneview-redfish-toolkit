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

import json
import unittest
from unittest import mock

from flask import Flask
from flask_api import status
from oneview_redfish_toolkit import util

from oneview_redfish_toolkit.blueprints.chassis_collection \
    import chassis_collection


class TestChassisCollection(unittest.TestCase):
    """Tests for ChassisCollection blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    @mock.patch.object(util, 'get_oneview_client')
    def setUp(self, ov_mock, get_oneview_mock):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.ini')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(
            chassis_collection,
            url_prefix='/redfish/v1/Chassis/')

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_chassis_collection_empty(self, mock_get_ov_client):
        """Tests ChassisCollection with an empty list"""

        client = mock_get_ov_client()
        client.server_hardware.get_all.return_value = []
        client.enclosures.get_all.return_value = []
        client.racks.get_all.return_value = []

        response = self.app.get("/redfish/v1/Chassis/")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        chassis_collection_members = json.loads(
            response.data.decode("utf-8"))['Members']
        self.assertEqual([], chassis_collection_members)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_chassis_collection_fail(self, mock_get_ov_client):
        """Tests ChassisCollection with an error"""

        client = mock_get_ov_client()
        client.server_hardware.get_all.side_effect = Exception()

        response = self.app.get("/redfish/v1/Chassis/")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_chassis_collection(self, mock_get_ov_client):
        """Tests ChassisCollection with a known Server Hardware list"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups/'
            'ServerHardwares.json'
        ) as f:
            server_hardware = json.load(f)

        # Loading enclosures mockup value
        with open(
            'oneview_redfish_toolkit/mockups/'
            'Enclosures.json'
        ) as f:
            enclosures = json.load(f)

        # Loading racks mockup value
        with open(
            'oneview_redfish_toolkit/mockups/'
            'Racks.json'
        ) as f:
            racks = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/ChassisCollection.json'
        ) as f:
            chassis_collection_json = f.read()

        # Create mock response
        client = mock_get_ov_client()
        client.server_hardware.get_all.return_value = server_hardware
        client.enclosures.get_all.return_value = enclosures
        client.racks.get_all.return_value = racks

        # Get ChassisCollection
        response = self.app.get("/redfish/v1/Chassis/")

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(chassis_collection_json, json_str)
