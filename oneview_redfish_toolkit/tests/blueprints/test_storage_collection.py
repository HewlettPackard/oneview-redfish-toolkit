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
from oneview_redfish_toolkit import util

# Module libs
from oneview_redfish_toolkit.blueprints.storage_collection \
    import storage_collection


class TestStorageCollection(unittest.TestCase):
    """Tests for StorageCollection blueprint"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Load config on util
        util.load_config('redfish.conf')

        # creates a test client
        self.app = Flask(__name__)

        self.app.register_blueprint(storage_collection)

        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_storage_collection(self):
        """Tests StorageCollection"""

        # Loading StorageCollection mockup result
        with open(
            'oneview_redfish_toolkit/mockups_redfish/StorageCollection.json'
        ) as f:
            storage_collection_mockup = f.read()

        # Get StorageCollection
        response = self.app.get(
            "/redfish/v1/Systems/30303437-3034-4D32-3230-313133364752/Storage"
        )

        # Gets json from response
        json_str = response.data.decode("utf-8")

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(storage_collection_mockup, json_str)
