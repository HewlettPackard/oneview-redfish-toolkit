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
import copy
import json

# 3rd party libs
from unittest import mock
from unittest.mock import call

from flask_api import status
from hpOneView.exceptions import HPOneViewException
from hpOneView.resources.servers.server_hardware_types import ServerHardwareTypes
from hpOneView.resources.servers.server_profiles import ServerProfiles
from hpOneView.resources.storage.volumes import Volumes
from hpOneView.resources.storage.storage_pools import StoragePools


# Module libs
from oneview_redfish_toolkit.api import volume
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
            'oneview_redfish_toolkit/mockups/oneview/DriveEnclosure.json'
        ) as f:
            self.drive_enclosures = json.load(f)
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

        with open(
            'oneview_redfish_toolkit/mockups/redfish/VolumeCollection.json'
        ) as f:
            self.volume_collection = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Volume.json'
        ) as f:
            self.volume = json.load(f)

        self.not_found_error = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'some message not found',
        })

        self.san_storage = {
            "hostOSType": "VMware (ESXi)",
            "manageSanStorage": True,
            "volumeAttachments": [
                {
                    "lunType": "Auto",
                    "volumeUri": "/rest/storage-volumes/" +
                    "B526F59E-9BC7-467F-9205-A9F4015CE296",
                    "volumeStorageSystemUri": "/rest/storage-systems/"
                    "TXQ1000307",
                    "storagePaths": [
                        {
                            "targetSelector": "Auto",
                            "isEnabled": True,
                            "connectionId": 2,
                            "targets": [
                            ]
                        }
                    ]
                }
            ]
        }

    def test_get_storage(self):
        """Tests Storage"""
        server_hardware_type_obj = ServerHardwareTypes(
            self.oneview_client, self.server_hardware_type)
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)

        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.server_hardware_types.get_by_uri.return_value \
            = server_hardware_type_obj
        self.oneview_client.\
            sas_logical_jbods.get.side_effect = self.logical_jbods

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
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware_types.get_by_uri.assert_called_with(
            self.server_hardware_type["uri"])
        self.oneview_client.sas_logical_jbods.get.assert_has_calls(
            [
                call(self.logical_jbods[0]["uri"]),
                call(self.logical_jbods[1]["uri"])
            ]
        )

    def test_get_storage_when_profile_not_found(self):
        """Tests when server profile not found"""

        self.oneview_client.\
            server_profiles.get_by_id.side_effect = self.not_found_error

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_storage_when_get_profile_raises_any_exception(self):
        """Tests when the searching of server profile raises an error"""

        self.oneview_client.server_profiles.get.side_effect = Exception

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

    def test_get_storage_when_hardware_type_not_found(self):
        """Tests when server hardware type not found"""

        self.oneview_client.server_hardware_types.get_by_uri.side_effect = \
            self.not_found_error

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_storage_when_hardware_type_raises_any_exception(self):
        """Tests when the searching of server hardware type raises an error"""

        self.oneview_client.server_hardware_types.get_by_uri.side_effect = Exception

        # Get Storage
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_drive(self):
        """Tests get a valid Drive"""
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.\
            sas_logical_jbods.get.side_effect = self.logical_jbods

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.drive_mockup, result)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.sas_logical_jbods.get.assert_has_calls(
            [
                call(self.logical_jbods[0]["uri"]),
                call(self.logical_jbods[1]["uri"])
            ]
        )

    def test_get_drive_when_profile_not_found(self):
        """Tests when server profile not found"""

        self.oneview_client.server_profiles.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.sas_logical_jbods.get.assert_not_called()

    def test_get_drive_when_profile_raises_any_exception(self):
        """Tests when the searching of server profile raises any error"""

        self.oneview_client.server_profiles.get_by_id.side_effect = Exception

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR,
                         response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.sas_logical_jbods.get.assert_not_called()

    def test_get_drive_when_sas_logical_jbod_not_found(self):
        """Tests when sas logical jbod not found"""
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.sas_logical_jbods.get.side_effect = \
            self.not_found_error

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/4"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.sas_logical_jbods.get.assert_called_with(
            self.logical_jbods[0]["uri"]
        )

    def test_get_drive_when_drive_not_found(self):
        """Tests when drive id can't be found"""
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.\
            sas_logical_jbods.get.side_effect = self.logical_jbods

        # we have the 4 drives, so id '5' is invalid
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/5"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Drive 5 not found", str(response.data))
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.sas_logical_jbods.get.assert_has_calls(
            [
                call(self.logical_jbods[0]["uri"]),
                call(self.logical_jbods[1]["uri"])
            ]
        )

    def test_get_drive_when_drive_id_is_invalid(self):
        """Tests when drive id is not a number"""
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        self.oneview_client.\
            server_profiles.get.return_value = profile_obj
        self.oneview_client.\
            sas_logical_jbods.get.side_effect = self.logical_jbods

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Drives/abc"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Drive id should be a integer", str(response.data))
        self.oneview_client.server_profiles.get_by_id.assert_not_called()
        self.oneview_client.sas_logical_jbods.get.assert_not_called()

    def test_composed_system_without_drives(self):
        """Tests Storage when it does not have drives"""
        server_profile = copy.deepcopy(self.server_profile)
        server_profile["localStorage"]["sasLogicalJBODs"] = []
        storage_mockup_without_drives = copy.deepcopy(self.storage_mockup)
        storage_mockup_without_drives["Drives"] = []
        storage_mockup_without_drives["Drives@odata.count"] = 0
        del storage_mockup_without_drives["Volumes"]
        profile_obj = ServerProfiles(self.oneview_client, server_profile)
        self.oneview_client.server_profiles.get_by_id.return_value = profile_obj
        server_hardware_type_obj = ServerHardwareTypes(
            self.oneview_client, self.server_hardware_type)
        self.oneview_client.server_hardware_types.get_by_uri.return_value \
            = server_hardware_type_obj

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1"
        )

        # Gets json from response
        result = json.loads(response.data.decode("utf-8"))

        # Tests response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(storage_mockup_without_drives, result)
        self.oneview_client.server_profiles.get_by_id.assert_called_with(
            self.server_profile["uuid"])
        self.oneview_client.server_hardware_types.get_by_uri.assert_called_with(
            self.server_hardware_type["uri"])
        self.oneview_client.sas_logical_jbods.get.assert_not_called()

    def test_get_volumeCollection(self):
        """Tests for get volume collection"""
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes"
        )
        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.volume_collection, result)

    def test_get_volumeCollection_without_volumes(self):
        """Tests when volume is not found"""

        server_profile = copy.deepcopy(self.server_profile)

        server_profile["localStorage"]["sasLogicalJBODs"] = []
        profile_obj = ServerProfiles(self.oneview_client, server_profile)
        self.oneview_client.server_profiles.get.return_value = profile_obj

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch.object(volume, "get_drive_path_from_logical_Drive_Bay_Uri")
    @mock.patch.object(volume, "get_drive_enclosure_uri_from_sas_Logical_"
                       "Interconnect")
    def test_get_volume(self, get_drive_enclosure_uri, get_drive_mock):
        """Tests for get volume"""
        profile_obj = ServerProfiles(self.oneview_client, self.server_profile)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.sas_logical_jbods.get.return_value = {
            "sasLogicalInterconnectUri": "/rest/sas-logical-interconnects/"
            "63138084-6d81-4b50-b35b-7e01a2390636",
            "logicalDriveBayUris": ["/rest/sas-logical-interconnects/63138084-"
                                    "6d81-4b50-b35b-7e01a2390636/logical-"
                                    "drive-enclosures/0d1d9142-f5fe-4256-"
                                    "aff2-d2dd95a0ce8f/logical-drive-bays"
                                    "/cef5316d-e5ab-4d46-83bc-caba10d954a8",
                                    "/rest/sas-logical-interconnects/63138084-"
                                    "6d81-4b50-b35b-7e01a2390636/logical-drive"
                                    "-enclosures/0d1d9142-f5fe-4256-aff2-d2dd9"
                                    "5a0ce8f/logical-drive-bays/3918cd02-7c70"
                                    "-4ef4-9936-ef6bad38c534"

                                    ],
            "maxSizeGB": 3276,
            "status": "OK",
            "name": "SSD_storage",
            "uri": "/rest/sas-logical-jbods/473db373-2d9c-4e7f-adca-"
            "a3649df5425d"
            }
        get_drive_mock.return_value = "1:1:1"
        get_drive_enclosure_uri.return_value = "/rest/drive-enclosures/"
        "SN123100"

        self.oneview_client.\
            drive_enclosures.get.return_value = self.drive_enclosures
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/1"
        )
        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.volume, result)

    @mock.patch.object(volume, "get_drive_path_from_logical_Drive_Bay_Uri")
    @mock.patch.object(volume, "get_drive_enclosure_uri_from_sas_Logical_"
                       "Interconnect")
    def test_get_volume_with_controllers_with_RAID(self,
                                                   get_drive_enclosure_uri,
                                                   get_drive_path_mock):
        """Tests for get volume with controllers"""

        server_profile = copy.deepcopy(self.server_profile)
        expected_result = copy.deepcopy(self.volume)
        expected_result["VolumeType"] = "Mirrored"
        temp = {}
        temp["deviceSlot"] = "Mezz 1"
        temp["mode"] = "Mixed"
        temp["initialize"] = False
        temp["logicalDrives"] = list()
        tempdict = {}
        tempdict["name"] = None
        tempdict["raidLevel"] = "RAID1"
        tempdict["bootable"] = True
        tempdict["numPhysicalDrives"] = None
        tempdict["driveTechnology"] = None
        tempdict["sasLogicalJBODId"] = 1
        tempdict["driveNumber"] = 1
        temp["logicalDrives"].append(tempdict)
        server_profile["localStorage"]["controllers"].append(temp)
        profile_obj = ServerProfiles(self.oneview_client, server_profile)
        self.oneview_client.\
            server_profiles.get_by_id.return_value = profile_obj
        self.oneview_client.sas_logical_jbods.get.return_value = {
            "sasLogicalInterconnectUri": "/rest/sas-logical-interconnects/"
            "63138084-6d81-4b50-b35b-7e01a2390636",
            "logicalDriveBayUris": ["/rest/sas-logical-interconnects/63138084-"
                                    "6d81-4b50-b35b-7e01a2390636/logical-"
                                    "drive-enclosures/0d1d9142-f5fe-4256-"
                                    "aff2-d2dd95a0ce8f/logical-drive-bays"
                                    "/cef5316d-e5ab-4d46-83bc-caba10d954a8",
                                    "/rest/sas-logical-interconnects/63138084-"
                                    "6d81-4b50-b35b-7e01a2390636/logical-drive"
                                    "-enclosures/0d1d9142-f5fe-4256-aff2-d2dd9"
                                    "5a0ce8f/logical-drive-bays/3918cd02-7c70"
                                    "-4ef4-9936-ef6bad38c534"

                                    ],
            "maxSizeGB": 3276,
            "status": "OK",
            "name": "SSD_storage",
            "uri": "/rest/sas-logical-jbods/473db373-2d9c-4e7f-adca-"
            "a3649df5425d"
            }
        get_drive_path_mock.return_value = "1:1:1"
        get_drive_enclosure_uri.return_value = "/rest/drive-enclosures/"
        "SN123100"

        self.oneview_client.\
            drive_enclosures.get.return_value = self.drive_enclosures
        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/1"
        )
        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_result, result)

    def test_get_volume_without_volumes(self):
        """Tests get volume when volume is not found"""

        server_profile = copy.deepcopy(self.server_profile)
        server_profile["localStorage"]["sasLogicalJBODs"] = []
        profile_obj = ServerProfiles(self.oneview_client, server_profile)
        self.oneview_client.server_profiles.get.return_value = profile_obj

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/1"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_external_storage_volumes(self):
        """Tests get external storage volume for computer system"""

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'VolumesResourceBlock.json'
        ) as f:
            expected_storage_details = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Volumes.json'
        ) as f:
            volume = json.load(f)

        expected_storage_details["@odata.id"] = "/redfish/v1/Systems/" + \
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/" + \
            "B526F59E-9BC7-467F-9205-A9F4015CE296"
        expected_storage_details["Id"] = \
            "B526F59E-9BC7-467F-9205-A9F4015CE296"

        storage_pool_obj = StoragePools(self.oneview_client, {
            "uri": "/rest/storage-pools/DC8BD64B-9A4E-4722-92D3-A9F4015B0B71",
            "deviceSpecificAttributes": {"supportedRAIDLevel": "RAID6"}
        })

        self.oneview_client.storage_pools.get_by_uri.return_value = storage_pool_obj
        server_profile = copy.deepcopy(self.server_profile)
        server_profile["sanStorage"] = self.san_storage

        profile_obj = ServerProfiles(self.oneview_client, server_profile)
        self.oneview_client.server_profiles.get_by_id.return_value = profile_obj
        volume_obj = Volumes(self.oneview_client, volume[0])
        self.oneview_client.volumes.get_by_id.return_value = volume_obj

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/"
            "B526F59E-9BC7-467F-9205-A9F4015CE296"
        )

        result = json.loads(response.data.decode("utf-8"))
        print(result)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(expected_storage_details, result)

    def test_get_volumes_when_volume_not_found(self):
        server_profile = copy.deepcopy(self.server_profile)
        server_profile["sanStorage"] = self.san_storage

        response = self.client.get(
            "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/"
            "wrong_uuid"
        )

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        msg_error = "Volume wrong_uuid not found for Storage 1 of System " \
                    "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        self.assertIn(msg_error, str(result))
