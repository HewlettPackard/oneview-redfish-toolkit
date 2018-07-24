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

from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection
from oneview_redfish_toolkit.api import status_mapping


class StorageCompositionDetails(RedfishJsonValidator):
    """Creates a StorageCompositionDetails dict

            Populates self.redfish with data retrieved from
            an OneView's Drive
    """

    SCHEMA_NAME = 'Storage'

    def __init__(self, drive):
        """StorageCompositionDetails constructor

            Populates self.redfish with the contents of devices from an
            Oneview's Drive

            Args:
                drive: Oneview's Drive dict
        """
        super().__init__(self.SCHEMA_NAME)

        drive_uuid = drive["uri"].split("/")[-1]
        self.odata_id = "{}/{}/Storage/1"\
            .format(ResourceBlockCollection.BASE_URI, drive_uuid)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = "1"
        self.redfish["Name"] = drive["name"]
        self.redfish["Status"] = status_mapping.STATUS_MAP.get(drive["status"])
        self.redfish["Drives"] = [
            {
                "@odata.id": self.odata_id + "/Drives/1"
            }
        ]
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Storage.Storage"

        self.redfish["@odata.id"] = self.odata_id

        self._validate()
