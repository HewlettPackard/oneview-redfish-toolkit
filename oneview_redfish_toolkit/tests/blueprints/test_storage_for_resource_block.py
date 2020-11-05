# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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

import json

from flask_api import status

from hpOneView.exceptions import HPOneViewException
from hpOneView.resources.storage.volumes import Volumes
from hpOneView.resources.storage.storage_pools import StoragePools

from oneview_redfish_toolkit.blueprints import storage_for_resource_block
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestStorageCompositionDetails(BaseFlaskTest):
    """Tests for StorageCompositionDetails blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestStorageCompositionDetails, self).setUpClass()

        self.app.register_blueprint(
            storage_for_resource_block.storage_for_resource_block)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drive.json'
        ) as f:
            self.drive = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Volumes.json'
        ) as f:
            self.volume = json.load(f)

    def test_get_storage_details(self):
        self.oneview_client.index_resources.get.return_value = self.drive

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'StorageForResourceBlock.json'
        ) as f:
            expected_storage_details = json.load(f)

        resource_not_found = HPOneViewException({
            "errorCode": "RESOURCE_NOT_FOUND",
            "message": "Any resource not found message"
        })

        self.oneview_client.volumes.get_by_id.side_effect = resource_not_found

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e/Storage/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_storage_details, result)

    def test_get_storage_details_when_it_is_not_found(self):
        self.oneview_client.index_resources.get.return_value = self.drive

        wrong_id = "2"  # any value other than "1"

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e/Storage/" + wrong_id)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        msg_error = "Storage 2 not found for ResourceBlock " \
                    "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e"
        self.assertIn(msg_error, str(result))

    def test_get_storage_drive_details(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'DriveForResourceBlock.json'
        ) as f:
            expected_drive_details = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/DriveEnclosure.json'
        ) as f:
            drive_enclosure = json.load(f)

        self.oneview_client.index_resources.get.return_value = self.drive
        self.oneview_client.drive_enclosures.get.return_value = drive_enclosure

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e/Storage/1/Drives/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_drive_details, result)

    def test_get_storage_drive_details_when_drive_is_not_found(self):
        self.oneview_client.index_resources.get.return_value = self.drive

        wrong_id = "2"  # any value other than "1"

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e/Storage/1/Drives/"
            + wrong_id)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        msg_error = "Drive 2 not found for Storage 1 of ResourceBlock " \
                    "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e"
        self.assertIn(msg_error, str(result))

    def test_get_storage_drive_details_when_storage_is_not_found(self):
        self.oneview_client.index_resources.get.return_value = self.drive

        wrong_id = "2"  # any value other than "1"

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e/Storage/{}/Drives/1"
            .format(wrong_id))

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        msg_error = "Storage 2 not found for ResourceBlock " \
                    "c4f0392d-fae9-4c2e-a2e6-b22e6bb7533e"
        self.assertIn(msg_error, str(result))

    def test_get_external_storage_details(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ExternalStorageForResourceBlock.json'
        ) as f:
            expected_storage_details = json.load(f)

        volume_obj = Volumes(self.oneview_client, self.volume[0])
        self.oneview_client.volumes.get_by_id.return_value = volume_obj

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/B526F59E-9BC7-467F-9205-A9F4015CE296/Storage/1")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_storage_details, result)

    def test_external_storage_resource_block(self):
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'VolumesResourceBlock.json'
        ) as f:
            expected_storage_details = json.load(f)

        volume_obj = Volumes(self.oneview_client, self.volume[0])
        self.oneview_client.volumes.get_by_id.return_value = volume_obj

        storage_pool = {
            "uri": "/rest/storage-pools/DC8BD64B-9A4E-4722-92D3-A9F4015B0B71",
            "deviceSpecificAttributes": {"supportedRAIDLevel": "RAID6"}
        }
        storage_pools_obj = StoragePools(self.oneview_client, storage_pool)
        self.oneview_client.storage_pools.get_by_uri.return_value = storage_pools_obj

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/B526F59E-9BC7-467F-9205-A9F4015CE296/Storage/1/Volumes/1")

        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_storage_details, result)

    def test_get_external_storage_details_when_storage_is_not_found(self):
        volume_obj = Volumes(self.oneview_client, self.volume[0])
        self.oneview_client.volumes.get_by_id.return_value = volume_obj

        wrong_id = "2"  # any value other than "1"

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/B526F59E-9BC7-467F-9205-A9F4015CE296/Storage/{}/Volumes/1"
            .format(wrong_id))

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        msg_error = "Storage 2 not found for ResourceBlock " \
                    "B526F59E-9BC7-467F-9205-A9F4015CE296"
        self.assertIn(msg_error, str(result))

    def test_get_external_storage_details_when_volume_is_not_found(self):
        volume_obj = Volumes(self.oneview_client, self.volume[0])
        self.oneview_client.volumes.get_by_id.return_value = volume_obj

        wrong_id = "2"  # any value other than "1"

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceBlocks"
            "/B526F59E-9BC7-467F-9205-A9F4015CE296/Storage/1/Volumes/{}"
            .format(wrong_id))

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        msg_error = "Volume 2 not found for Storage 1 of ResourceBlock " \
                    "B526F59E-9BC7-467F-9205-A9F4015CE296"
        self.assertIn(msg_error, str(result))
