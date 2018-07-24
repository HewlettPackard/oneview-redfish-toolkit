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


class StorageDriveCompositionDetails(RedfishJsonValidator):
    """Creates a StorageDriveCompositionDetails dict

            Populates self.redfish with data retrieved from
            an OneView's Drive
    """

    SCHEMA_NAME = 'Drive'

    def __init__(self, drive, drive_enclosure):
        """StorageDriveCompositionDetails constructor

            Populates self.redfish with the contents of drive from an
            Oneview's Drive

            Args:
                drive: Oneview's Drive dict
                drive_enclosure: Oneview's Drive Enclosure dict
        """
        super().__init__(self.SCHEMA_NAME)

        enclosure_id = drive_enclosure["enclosureUri"].split("/")[-1]
        drive_uuid = drive["uri"].split("/")[-1]

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = "1"
        self.redfish["Name"] = drive["name"]
        self.redfish["Status"] = status_mapping.STATUS_MAP.get(drive["status"])

        attributes = drive["attributes"]
        size_in_bytes = float(attributes["capacityInGB"]) \
            * 1024 * 1024 * 1024
        self.redfish["CapacityBytes"] = int(size_in_bytes)
        self.redfish["Protocol"] = attributes["interfaceType"]
        self.redfish["MediaType"] = attributes["mediaType"]
        self.redfish["Links"] = {
            "Chassis": {
                "@odata.id": "/redfish/v1/Chassis/" + enclosure_id
            }
        }
        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Drive.Drive"

        self.redfish["@odata.id"] = "{}/{}/Storage/1/Drives/1"\
            .format(ResourceBlockCollection.BASE_URI, drive_uuid)

        self._validate()
