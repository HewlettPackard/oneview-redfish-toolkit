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
from unittest import mock

from flask import Flask

from oneview_redfish_toolkit.blueprints.service_root import service_root
from oneview_redfish_toolkit import util


class TestServiceRoot(unittest.TestCase):
    """Tests from ServiceRoot blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, mock_ov):
        """Tests ComputerSystemCollection bueprint"""

        # Load config on util
        util.load_config('oneview_redfish_toolkit/redfish.ini')

        # creates a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(
            service_root,
            url_prefix='/redfish/v1/'
        )
        # creates a test client
        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_service_root(self):
        """Tests ServiceRoot blueprint result against know value """
        result = self.app.get("/redfish/v1/")

        json_str = result.data.decode("utf-8")

        with open(
            'oneview_redfish_toolkit/mockups/ServiceRoot.json'
        ) as f:
            mok_json = f.read()
        self.assertEqual(json_str, mok_json)
