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

import json

from unittest import mock

from oneview_redfish_toolkit.api import volume

from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestVolume(BaseTest):
    """Tests for Volume class"""

    def test_get_device_slot_from_sas_logical_jbod_by_volumeid(self):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            server_profile = json.load(f)

        volumeobj = \
            volume.get_device_slot_from_sas_logical_jbod_by_volumeid(
                server_profile, '1')

        self.assertEqualMockup('Mezz 1', volumeobj)

    def test_get_device_slot_from_sas_logical_jbod_when_volumeid_not_found(
            self):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            server_profile = json.load(f)

        volumeobj = volume.get_device_slot_from_sas_logical_jbod_by_volumeid(
            server_profile, '3')

        self.assertEqualMockup(None, volumeobj)

    def test_get_capacity_in_bytes(self):

        volumeobj = \
            volume.get_capacity_in_bytes('3276')

        self.assertEqualMockup(3517578215424, volumeobj)

    @mock.patch.object(volume, "get_raid_level_for_storage_volume")
    def test_build_external_storage_volume_details(self, mock_get_raid_level):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/Volumes.json'
        ) as f:
            volume_data = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'VolumesResourceBlock.json'
        ) as f:
            expected_result = json.load(f)

        expected_result["@odata.id"] = "/redfish/v1/Systems/" + \
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/" + \
            "B526F59E-9BC7-467F-9205-A9F4015CE296"

        expected_result["Id"] = \
            "B526F59E-9BC7-467F-9205-A9F4015CE296"

        expected_result["VolumeType"] = "RawDevice"
        mock_get_raid_level.return_value = None

        sp_uuid = "b425802b-a6a5-4941-8885-aab68dfa2ee2"
        volume_id = "B526F59E-9BC7-467F-9205-A9F4015CE296"
        result = volume.Volume.build_external_storage_volume_details(
            sp_uuid, volume_data[0], volume_id)

        volume_result = json.loads(result.serialize())

        self.assertEqualMockup(expected_result, volume_result)
