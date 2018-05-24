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
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints import service_root
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
        self.app.register_blueprint(
            service_root.service_root, url_prefix='/redfish/v1/')

        @self.app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        def internal_server_error(error):
            """Creates an Internal Server Error response"""

            redfish_error = RedfishError(
                "InternalError",
                "The request failed due to an internal service error.  "
                "The service is still operational.")
            redfish_error.add_extended_info("InternalError")
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype="application/json")

        # creates a test client
        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch.object(service_root, 'g')
    def test_service_root_oneview_exception(self, g):
        """Tests ServiceROOT with an exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'appliance error',
        })

        g.oneview_client.appliance_node_information.get_version.side_effect = e

        response = self.app.get("/redfish/v1/")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )

        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(service_root, 'g')
    def test_service_root_exception(self, g):
        """Tests ServiceROOT with an exception"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'appliance error',
        })

        g.oneview_client.appliance_node_information.get_version.side_effect = e

        response = self.app.get("/redfish/v1/")

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )

        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(util, 'config')
    @mock.patch.object(service_root, 'g')
    def test_get_service_root(self, g, config_mock):
        """Tests ServiceRoot blueprint result against know value """

        def side_effect(section, option):
            if section == "redfish" and option == "authentication_mode":
                return "conf"
            else:
                return util.config.get(section, option)

        g.oneview_client.appliance_node_information.get_version.return_value = \
            {'uuid': '00000000-0000-0000-0000-000000000000'}
        config_mock.get.side_effect = side_effect

        result = self.app.get("/redfish/v1/")

        result = json.loads(result.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ServiceRoot.json'
        ) as f:
            service_root_mockup = json.load(f)
        self.assertEqual(service_root_mockup, result)
