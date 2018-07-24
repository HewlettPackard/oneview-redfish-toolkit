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
from unittest import mock

# 3rd party libs
from unittest.mock import call

from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Module libs
from oneview_redfish_toolkit.blueprints import storage
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestStorage(BaseFlaskTest):
    """Tests for Storage blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestStorage, self).setUpClass()

        self.app.register_blueprint(storage.storage)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwareTypes.json'
        ) as f:
            self.server_hardware_type = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'SASLogicalJBODListForStorage.json'
        ) as f:
            self.logical_jbods = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Storage.json'
        ) as f:
            self.storage_mockup = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/redfish/Drive.json'
        ) as f:
            self.drive_mockup = json.load(f)

        self.not_found_error = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'some message not found',
        })

    @mock.patch.object(storage, 'g')
    def test_get_storage(self, g):
        """Tests Storage"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.server_hardware_types.get.return_value \
            = self.server_hardware_type
        g.oneview_client.sas_logical_jbods.get.side_effect = self.logical_jbods

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.storage_mockup, result)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        g.oneview_client.server_hardware_types.get.assert_called_with(
            self.server_hardware_type["uri"])
        g.oneview_client.sas_logical_jbods.get.assert_has_calls(
            [
                call(self.logical_jbods[0]["uri"]),
                call(self.logical_jbods[1]["uri"])
            ]
        )

    @mock.patch.object(storage, 'g')
    def test_get_storage_when_profile_not_found(self, g):
        """Tests when server profile not found"""

        g.oneview_client.server_profiles.get.side_effect = self.not_found_error

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(storage, 'g')
    def test_get_storage_when_get_profile_raises_any_exception(self, g):
        """Tests when the searching of server profile raises an error"""

        g.oneview_client.server_profiles.get.side_effect = Exception

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(storage, 'g')
    def test_get_storage_when_hardware_type_not_found(self, g):
        """Tests when server hardware type not found"""

        g.oneview_client.server_hardware_types.get.side_effect = \
            self.not_found_error

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(storage, 'g')
    def test_get_storage_when_hardware_type_raises_any_exception(self, g):
        """Tests when the searching of server hardware type raises an error"""

        g.oneview_client.server_hardware_types.get.side_effect = Exception

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(storage, 'g')
    def test_get_drive(self, g):
        """Tests get a valid Drive"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.sas_logical_jbods.get.side_effect = self.logical_jbods

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.drive_mockup, result)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        g.oneview_client.sas_logical_jbods.get.assert_has_calls(
            [
                call(self.logical_jbods[0]["uri"]),
                call(self.logical_jbods[1]["uri"])
            ]
        )

    @mock.patch.object(storage, 'g')
    def test_get_drive_when_profile_not_found(self, g):
        """Tests when server profile not found"""

        g.oneview_client.server_profiles.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        g.oneview_client.sas_logical_jbods.get.assert_not_called()

    @mock.patch.object(storage, 'g')
    def test_get_drive_when_profile_raises_any_exception(self, g):
        """Tests when the searching of server profile raises any error"""

        g.oneview_client.server_profiles.get.side_effect = Exception

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR,
                         response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        g.oneview_client.sas_logical_jbods.get.assert_not_called()

    @mock.patch.object(storage, 'g')
    def test_get_drive_when_sas_logical_jbod_not_found(self, g):
        """Tests when sas logical jbod not found"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.sas_logical_jbods.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        g.oneview_client.sas_logical_jbods.get.assert_called_with(
            self.logical_jbods[0]["uri"]
        )

    @mock.patch.object(storage, 'g')
    def test_get_drive_when_drive_not_found(self, g):
        """Tests when drive id can't be found"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.sas_logical_jbods.get.side_effect = self.logical_jbods

        # we have the 4 drives, so id '5' is invalid
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/5"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Drive 5 not found", str(response.data))
        g.oneview_client.server_profiles.get.assert_called_with(
            self.server_profile["uuid"])
        g.oneview_client.sas_logical_jbods.get.assert_has_calls(
            [
                call(self.logical_jbods[0]["uri"]),
                call(self.logical_jbods[1]["uri"])
            ]
        )

    @mock.patch.object(storage, 'g')
    def test_get_drive_when_drive_id_is_invalid(self, g):
        """Tests when drive id is not a number"""

        g.oneview_client.server_profiles.get.return_value = self.server_profile
        g.oneview_client.sas_logical_jbods.get.side_effect = self.logical_jbods

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/abc"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Drive id should be a integer", str(response.data))
        g.oneview_client.server_profiles.get.assert_not_called()
        g.oneview_client.sas_logical_jbods.get.assert_not_called()
