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

import unittest

from flask import Flask
from flask_api import status

from oneview_redfish_toolkit.blueprints.redfish_base import redfish_base


class TestRedfishBase(unittest.TestCase):

    def setUp(self):

        self.app = Flask(__name__)
        self.app.register_blueprint(redfish_base)
        # creates a test client
        self.app = self.app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_redfish_base_status(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get("/redfish/")

        # assert the status code of the response
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_get_redfish_base_response(self):
        result = self.app.get("/redfish/")

        json_str = result.data.decode("utf-8")

        self.assertEqual(json_str, '{"v1": "/redfish/v1/"}')
