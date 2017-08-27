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

from flask import Response
from flask_api import status

import json

from oneview_redfish_toolkit.app import app
import oneview_redfish_toolkit.blueprints.computer_system_collection \
    as computer_system_collection

import unittest
from unittest import mock


class TestComputerSystemCollection(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(computer_system_collection, 'get_ov_client')
    def test_get_computer_system_collection_empty(self, mock_get_ov_client):
        client = mock_get_ov_client()
        client.server_hardware.get_all.return_value = []

        response = self.app.get("/redfish/v1/Systems/")

        expected_response = Response(
            response="",
            status=status.HTTP_200_OK,
            mimetype="application/json")

        self.assertEqual(expected_response.status, response.status)
        self.assertEqual(expected_response.mimetype, response.mimetype)
        computer_systems = json.loads(response.data.decode("utf-8"))['Members']
        self.assertEqual([], computer_systems)

    @mock.patch.object(computer_system_collection, 'get_ov_client')
    def test_get_computer_system_collection_fail(self, mock_get_ov_client):
        client = mock_get_ov_client()
        exc = OSError()
        client.server_hardware.get_all.side_effect = exc

        response = self.app.get("/redfish/v1/Systems/")

        expected_response = Response(
            response="",
            status=status.HTTP_404_NOT_FOUND,
            mimetype="application/json")

        self.assertEqual(expected_response.status, response.status)
        self.assertEqual(expected_response.mimetype, response.mimetype)

    @mock.patch.object(computer_system_collection, 'get_ov_client')
    def test_get_computer_system_collection(self, mock_get_ov_client):
        client = mock_get_ov_client()

        with open(
                'oneview_redfish_toolkit/mockups/'
                'ServerHardwares.json'
        ) as f:
            fake_server_hardwares = json.loads(f.read())
            client.server_hardware.get_all.return_value = fake_server_hardwares

        response = self.app.get("/redfish/v1/Systems/")

        expected_response = Response(
            response="",
            status=status.HTTP_200_OK,
            mimetype="application/json")

        self.assertEqual(expected_response.status, response.status)
        self.assertEqual(expected_response.mimetype, response.mimetype)
        computer_systems = json.loads(response.data.decode("utf-8"))['Members']
        self.assertNotEqual([], computer_systems)
