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

# 3rd party libs
from flask import Flask
from flask_api import status

# Module libs
from oneview_redfish_toolkit.blueprints.odata import odata


class TestOdata(unittest.TestCase):
    """Tests for Odata blueprint"""

    def setUp(self):
        """Tests Odata blueprint setup"""

        # creates a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(odata)
        # creates a test client
        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_odata(self):
        """Tests Odata blueprint result against know value """

        response = self.app.get("/redfish/v1/odata")

        json_str = response.data.decode("utf-8")

        with open(
            'oneview_redfish_toolkit/mockups_redfish/Odata.json'
        ) as f:
            odata_mockup = f.read()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(odata_mockup, json_str)
