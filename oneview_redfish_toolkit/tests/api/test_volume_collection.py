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

import copy
import json

from oneview_redfish_toolkit.api.volume_collection import VolumeCollection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestolumeCollection(BaseTest):
    """Tests for VolumeCollection class"""

    def setUp(self):
        """Tests preparation"""

        # Loading VolumeCollection mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/VolumeCollection.json'
        ) as f:
            self.volume_collection_mockup = json.load(f)
        with open(
            'oneview_redfish_toolkit/mockups/oneview/ServerProfile.json'
        ) as f:
            self.server_profile = json.load(f)

    def test_serialize(self):
        # Tests the serialize function result against known result

        server_profile = copy.deepcopy(self.server_profile)
        server_profile["sanStorage"]["volumeAttachments"] = [{
            "id": 1,
            "lun": "1",
            "lunType": "Auto",
            "status": "OK",
            "volumeUri": "/rest/storage-volumes/volumeUuid",
        }]
        volume = {
            "@odata.id": "/redfish/v1/Systems/"
            "b425802b-a6a5-4941-8885-aab68dfa2ee2/Storage/1/Volumes/volumeUuid"
        }
        volume_collection_mockup = copy.deepcopy(self.volume_collection_mockup)
        volume_collection_mockup["Members"].append(volume)
        volume_collection_mockup["Members@odata.count"] = 3
        volume_collection = \
            VolumeCollection(server_profile)

        result = json.loads(volume_collection.serialize())

        self.assertEqualMockup(volume_collection_mockup, result)
