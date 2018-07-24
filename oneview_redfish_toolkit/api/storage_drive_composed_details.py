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
from oneview_redfish_toolkit.api import status_mapping


class StorageDriveComposedDetails(RedfishJsonValidator):
    """Creates a Drive dict for a storage of a composed system

            Populates self.redfish with data retrieved from
            an OneView's Drive
    """

    SCHEMA_NAME = 'Drive'

    def __init__(self, drive_id, server_profile, logical_jbod):
        """StorageDriveComposedDetails constructor

            Populates self.redfish with the contents of drive from an
            Oneview's sas logical jbod and an Oneview's server profile

            Args:
                drive_id: id of redfish Drive
                server_profile: Oneview's server profile dict
                logical_jbod: Oneview's sas logical jbod dict
        """
        super().__init__(self.SCHEMA_NAME)

        enclosure_id = server_profile["enclosureUri"].split("/")[-1]
        profile_uuid = server_profile["uri"].split("/")[-1]

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = str(drive_id)
        self.redfish["Name"] = logical_jbod["name"]
        self.redfish["Status"] = status_mapping\
            .STATUS_MAP.get(logical_jbod["status"])

        size_in_bytes = float(logical_jbod["maxSizeGB"]) \
            * 1024 * 1024 * 1024
        self.redfish["CapacityBytes"] = int(size_in_bytes)
        self.redfish["Protocol"] = \
            logical_jbod["driveTechnology"]["deviceInterface"]
        self.redfish["MediaType"] = \
            logical_jbod["driveTechnology"]["driveMedia"]
        self.redfish["Links"] = {
            "Chassis": {
                "@odata.id": "/redfish/v1/Chassis/" + enclosure_id
            }
        }
        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Drive.Drive"

        self.redfish["@odata.id"] = "{}/{}/Storage/1/Drives/{}"\
            .format(ComputerSystem.BASE_URI, profile_uuid, drive_id)

        self._validate()
