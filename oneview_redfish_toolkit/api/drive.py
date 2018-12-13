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
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection
from oneview_redfish_toolkit.api import status_mapping


class Drive(RedfishJsonValidator):
    """Creates a StorageDriveCompositionDetails dict

            Populates self.redfish with data retrieved from
            an OneView's Drive
    """

    SCHEMA_NAME = 'Drive'
    METADATA_INFO = "/redfish/v1/$metadata#Drive.Drive"

    def __init__(self, data):
        """StorageDriveCompositionDetails constructor

            Populates self.redfish and validates the result

            Args:
                data: a dict with Redfish's Drive data
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()

        self.redfish.update(data)

        self.redfish["@odata.context"] = self.__class__.METADATA_INFO

        self._validate()

    @staticmethod
    def build_for_computer_system(drive_id, server_profile, logical_jbod):
        enclosure_id = server_profile["enclosureUri"].split("/")[-1]
        profile_uuid = server_profile["uri"].split("/")[-1]
        odata_id = "{}/{}/Storage/1/Drives/{}"\
            .format(ComputerSystem.BASE_URI, profile_uuid, drive_id)
        media_type = logical_jbod["driveTechnology"]["driveMedia"]
        media_type = None if (media_type == "Unknown") else media_type
        attrs = {
            "Id": str(drive_id),
            "Name": logical_jbod["name"],
            "Status": status_mapping.STATUS_MAP.get(logical_jbod["status"]),
            "CapacityBytes": Drive.get_capacity_in_bytes(
                logical_jbod["maxSizeGB"]),
            "Protocol": logical_jbod["driveTechnology"]["deviceInterface"],
            "MediaType": media_type,
            "Links": {
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/" + enclosure_id
                }
            },
            "@odata.id": odata_id
        }

        return Drive(attrs)

    @staticmethod
    def build_for_resource_block(drive, drive_enclosure):
        enclosure_id = drive_enclosure["enclosureUri"].split("/")[-1]
        drive_uuid = drive["uri"].split("/")[-1]
        ov_drive_attrs = drive["attributes"]
        odata_id = "{}/{}/Storage/1/Drives/1"\
            .format(ResourceBlockCollection.BASE_URI, drive_uuid)
        media_type = ov_drive_attrs["mediaType"]
        media_type = None if (media_type == "Unknown") else media_type
        attrs = {
            "Id": "1",
            "Name": drive["name"],
            "Status": status_mapping.STATUS_MAP.get(drive["status"]),
            "CapacityBytes": Drive.get_capacity_in_bytes(
                ov_drive_attrs["capacityInGB"]),
            "Protocol": ov_drive_attrs["interfaceType"],
            "MediaType": media_type,
            "Links": {
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/" + enclosure_id
                }
            },
            "@odata.id": odata_id
        }

        return Drive(attrs)

    @staticmethod
    def get_capacity_in_bytes(capacity_in_gb):
        size_in_bytes = float(capacity_in_gb) * 1024 * 1024 * 1024
        return int(size_in_bytes)
