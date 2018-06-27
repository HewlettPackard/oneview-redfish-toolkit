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

from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api import status_mapping


class StorageResourceBlock(ResourceBlock):
    """Creates a ResourceBlock Redfish dict for Storage Drive

        Populates self.redfish with Drive data retrieved from OneView.
    """

    def __init__(self, drive):
        """StorageResourceBlock constructor

            Populates self.redfish with the contents of drive

            Args:
                drive: OneView Drive dict
        """
        uuid = drive["uri"].split("/")[-1]
        super().__init__(uuid, drive)

        self.redfish["ResourceBlockType"] = ["Storage"]
        self.redfish["Status"] = status_mapping.STATUS_MAP.get(drive["status"])

        if drive["attributes"]["available"]:
            compositState = "Unused"
        else:
            compositState = "Composed"

        self.redfish["CompositionStatus"]["CompositionState"] = compositState

        self.redfish["Storage"] = [
            {
                "@odata.id": self.redfish["@odata.id"] + "/Storage/1"
            }
        ]

        self._validate()
