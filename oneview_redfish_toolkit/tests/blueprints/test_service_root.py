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
import unittest
from unittest import mock

# 3rd party libs
from flask import Flask
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints.service_root import service_root
from oneview_redfish_toolkit import util


class TestServiceRoot(unittest.TestCase):
    """Tests from ServiceRoot blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests ServiceRoot blueprint setup"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(service_root, url_prefix='/redfish/v1/')
        # creates a test client
        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(util, 'get_oneview_client')
    def test_service_root_oneview_exception(self, get_oneview_client_mockup):
        """Tests ServiceROOT with an exception"""

        oneview_client = get_oneview_client_mockup()
        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'appliance error',
        })

        oneview_client.appliance_node_information.get_version.side_effect = e

        response = self.app.get("/redfish/v1/")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )

        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_service_root_exception(self, get_oneview_client_mockup):
        """Tests ServiceROOT with an exception"""

        oneview_client = get_oneview_client_mockup()
        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'appliance error',
        })

        oneview_client.appliance_node_information.get_version.side_effect = e

        response = self.app.get("/redfish/v1/")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )

        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'get_oneview_client')
    def test_get_service_root(self, get_oneview_client_mockup):
        """Tests ServiceRoot blueprint result against know value """

        oneview_client = get_oneview_client_mockup()
        oneview_client.appliance_node_information.get_version.return_value = \
            {'uuid': '00000000-0000-0000-0000-000000000000'}

        result = self.app.get("/redfish/v1/")

        json_str = result.data.decode("utf-8")

        with open(
            'oneview_redfish_toolkit/mockups_redfish/ServiceRoot.json'
        ) as f:
            service_root_mockup = f.read()
        self.assertEqual(service_root_mockup, json_str)
