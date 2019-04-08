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

from oneview_redfish_toolkit.api.storage import Storage
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestStorage(BaseTest):
    """Tests for Storage class"""

    def test_build_for_composed_system(self):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            server_profile = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerHardwareTypes.json'
        ) as f:
            server_hardware_types = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'SASLogicalJBODListForStorage.json'
        ) as f:
            sas_logical_jbods = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Storage.json'
        ) as f:
            storage_mockup = json.load(f)

        storage = Storage.build_for_composed_system(server_profile,
                                                    server_hardware_types,
                                                    sas_logical_jbods)

        result = json.loads(storage.serialize())

        self.assertEqualMockup(storage_mockup, result)

    def test_build_for_resource_block(self):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/Drive.json'
        ) as f:
            drive = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'StorageForResourceBlock.json'
        ) as f:
            expected_result = json.load(f)

        storage = Storage.build_for_resource_block(drive)

        result = json.loads(storage.serialize())

        self.assertEqualMockup(expected_result, result)

    def test_build_for_resource_block_for_external_storage(self):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/Volumes.json'
        ) as f:
            volume = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'ExternalStorageForResourceBlock.json'
        ) as f:
            expected_result = json.load(f)

        storage = Storage.build_for_resource_block(volume[0])

        result = json.loads(storage.serialize())

        self.assertEqualMockup(expected_result, result)
