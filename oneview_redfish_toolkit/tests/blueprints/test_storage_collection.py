# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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

# 3rd party libs
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import storage_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestStorageCollection(BaseFlaskTest):
    """Tests for StorageCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestStorageCollection, self).setUpClass()

        self.app.register_blueprint(storage_collection.storage_collection)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/StorageCollection.json'
        ) as f:
            self.storage_collection_mockup = json.load(f)

    def test_get_storage_collection(self):
        """Tests StorageCollection"""

        self.oneview_client.\
            server_profiles.get.return_value = self.server_profile

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.storage_collection_mockup, result)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])

    def test_get_storage_collection_when_profile_not_found(self):
        """Tests StorageCollection"""

        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'server-hardware not found',
        })
        self.oneview_client.server_profiles.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])

    def test_get_storage_collection_when_profile_raises_any_exception(self):
        """Tests StorageCollection"""

        e = HPOneViewException({
            'errorCode': 'ANOTHER_ERROR',
            'message': 'server-hardware-types error',
        })
        self.oneview_client.server_profiles.get.side_effect = e

        response = self.client.get(
            "/redfish/v1/Systems/b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
