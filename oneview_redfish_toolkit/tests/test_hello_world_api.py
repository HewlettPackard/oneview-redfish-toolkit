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

"""
test_hello_world_api
----------------------------------

Tests for `oneview_redfish_toolkit` module.
"""

import json
import unittest

from oneview_redfish_toolkit.api.app import app


class HelloWorldAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_status_hello_world(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get("/api/")

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_response_hello_world(self):
        result = self.app.get("/api/")

        json_result = json.loads(result.data.decode("utf-8"))

        self.assertEqual(json_result["message"], "Hello World!")
