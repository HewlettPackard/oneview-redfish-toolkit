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

import collections
from functools import reduce
import operator

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection
import oneview_redfish_toolkit.api.status_mapping as status_mapping

DEVICE_PROTOCOLS_MAP = {
    "SasHdd": "SAS",
    "SasSsd": "SAS",
    "SataHdd": "SATA",
    "SataSsd": "SATA",
    "NVMeHdd": "NVMe",
    "NVMeSsd": "NVMe"
}


class Storage(RedfishJsonValidator):
    """Creates a Storage Redfish dict

        Populates self.redfish with Storage data
    """

    SCHEMA_NAME = 'Storage'
    METADATA_INFO = "/redfish/v1/$metadata#Storage.Storage"

    def __init__(self, data):
        """Storage constructor

            Populates self.redfish and validates the result

            Args:
                data: a dict with Redfish's Storage data
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish.update(data)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["@odata.context"] = self.__class__.METADATA_INFO

        self._validate()

    @staticmethod
    def _map_supported_device_protos(drive_technologies):
        supported_device_protocols = set()

        try:
            for drive_option in drive_technologies:
                supported_device_protocols.add(
                    DEVICE_PROTOCOLS_MAP[drive_option])
        except Exception:
            supported_device_protocols.add('')

        return supported_device_protocols

    @staticmethod
    def build_for_composed_system(server_profile, server_hardware_type,
                                  sas_logical_jbods,
                                  external_storage_volumes):
        """Returns a Storage with the contents of data from an Oneview

            Args:
                server_profile: Server Profile from Oneview
                server_hardware_type: Server Hardware Type from Oneview
                sas_logical_jbods: SAS Logical JBODs info from Oneview
                external_storage_volumes: Storage volumes from OneView
        """
        attrs = {}

        drive_technologies = \
            server_hardware_type['storageCapabilities']['driveTechnologies']

        attrs["@odata.id"] = \
            ComputerSystem.BASE_URI + "/" \
            + server_profile["uuid"] + "/Storage/1"
        attrs["StorageControllers@odata.count"] = 1
        attrs["Id"] = "1"
        attrs["Name"] = "Storage Controller"
        attrs["Status"] = collections.OrderedDict()
        ok_struct = status_mapping.STATUS_MAP.get("OK")
        attrs["Status"]["State"] = ok_struct["State"]
        attrs["Status"]["Health"] = ok_struct["Health"]
        attrs["StorageControllers"] = list()

        # adapter storage capabilities (if any)
        for adapter in server_hardware_type['adapters']:
            if adapter['storageCapabilities']:
                new_capability = collections.OrderedDict()
                new_capability["SupportedDeviceProtocols"] = sorted(
                    Storage._map_supported_device_protos(drive_technologies))
                attrs["StorageControllers"].append(new_capability)

        # internal storage capabilities
        storage_controllers = collections.OrderedDict()
        storage_controllers["Manufacturer"] = "HPE"
        storage_controllers["SupportedDeviceProtocols"] = \
            sorted(Storage._map_supported_device_protos(drive_technologies))
        attrs["StorageControllers"].append(storage_controllers)

        count_drives_by_jbod = \
            [int(item["numPhysicalDrives"]) for item in sas_logical_jbods]

        count_drives = reduce(operator.add, count_drives_by_jbod, 0)

        attrs["Drives@odata.count"] = count_drives
        attrs["Drives"] = list()
        for i in range(count_drives):
            drive_id = str(i + 1)
            attrs["Drives"].append({
                "@odata.id": attrs["@odata.id"] + "/Drives/" + drive_id
            })
        if len(sas_logical_jbods) != 0 or external_storage_volumes:
            attrs["Volumes"] = collections.OrderedDict()
            attrs["Volumes"]["@odata.id"] = attrs["@odata.id"] + "/Volumes"

        return Storage(attrs)

    @staticmethod
    def build_for_resource_block(storage_block):
        """Returns a Storage with the contents of devices from an

            Oneview's Drive or storage volume

            Args:
                storage_block: Oneview's Drive or Volume dict
        """
        attrs = {}

        drive_uuid = storage_block["uri"].split("/")[-1]
        odata_id = "{}/{}/Storage/1" \
            .format(ResourceBlockCollection.BASE_URI, drive_uuid)

        attrs["Id"] = "1"
        attrs["Name"] = storage_block["name"]
        attrs["Status"] = status_mapping.STATUS_MAP.get(
            storage_block["status"])

        if storage_block["category"] == "storage-volumes":
            attrs["Volumes"] = {
                "@data.id": odata_id + "/Volumes/1"
            }
        else:
            attrs["Drives"] = [
                {
                    "@odata.id": odata_id + "/Drives/1"
                }
            ]

        attrs["@odata.id"] = odata_id

        return Storage(attrs)
