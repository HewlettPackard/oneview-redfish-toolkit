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
from oneview_redfish_toolkit import util

# Module libs
from oneview_redfish_toolkit.blueprints.chassis_collection \
    import chassis_collection


class TestChassisCollection(unittest.TestCase):
    """Tests for ChassisCollection blueprint

        Tests:
            - server hardware empty
            - enclosures empty
            - racks empty
            - oneview unexpected exception
            - know chassis collection
    """

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(chassis_collection)

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_chassis_collection_unexpected_error(
            self, get_oneview_client_mockup):
        """Tests ChassisCollection with an error"""

        client = get_oneview_client_mockup()
        client.server_hardware.get_all.side_effect = Exception()

        response = self.app.get("/redfish/v1/Chassis/")

        json_str = response.data.decode("utf-8")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual('{"error": "Internal Server Error"}', json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_server_hardwares_empty(self, get_oneview_client_mockup):
        """Tests ChassisCollection with an empty server hardware list"""

        client = get_oneview_client_mockup()
        client.server_hardware.get_all.return_value = []

        response = self.app.get("/redfish/v1/Chassis/")

        json_str = response.data.decode("utf-8")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual('{"error": "Resource not found"}', json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_enclosures_empty(self, get_oneview_client_mockup):
        """Tests ChassisCollection with an empty enclosure list"""

        client = get_oneview_client_mockup()
        client.enclosures.get_all.return_value = []

        response = self.app.get("/redfish/v1/Chassis/")

        json_str = response.data.decode("utf-8")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual('{"error": "Resource not found"}', json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_racks_empty(self, get_oneview_client_mockup):
        """Tests ChassisCollection with an empty rack list"""

        client = get_oneview_client_mockup()
        client.racks.get_all.return_value = []

        response = self.app.get("/redfish/v1/Chassis/")

        json_str = response.data.decode("utf-8")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual('{"error": "Resource not found"}', json_str)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_chassis_collection(self, get_oneview_client_mockup):
        """Tests ChassisCollection with a known Results"""

        # Loading server_hardware mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/'
            'ServerHardwares.json'
        ) as f:
            server_hardwares = json.load(f)

        # Loading enclosures mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/'
            'Enclosures.json'
        ) as f:
            enclosures = json.load(f)

        # Loading racks mockup value
        with open(
            'oneview_redfish_toolkit/mockups_oneview/'
            'Racks.json'
        ) as f:
            racks = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups_redfish/'
                'ChassisCollection.json'
        ) as f:
            chassis_collection_mockup = f.read()

        # Create mock response
        client = get_oneview_client_mockup()
        client.server_hardware.get_all.return_value = server_hardwares
        client.enclosures.get_all.return_value = enclosures
        client.racks.get_all.return_value = racks

        # Get ChassisCollection
        response = self.app.get("/redfish/v1/Chassis/")

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(chassis_collection_mockup, json_str)
