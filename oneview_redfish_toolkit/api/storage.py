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

        Populates self.redfish with Storage data retrieved from OneView
    """

    SCHEMA_NAME = 'Storage'

    def __init__(self,
                 server_profile,
                 server_hardware_type,
                 sas_logical_jbods):
        """Storage constructor

            Populates self.redfish with the contents of Storage using
            Server Profile, Server Hardware Type and SAS Logical JBODs
            to do that

            Args:
                server_profile: Server Profile from Oneview
                server_hardware_type: Server Hardware Type from Oneview
                sas_logical_jbods: SAS Logical JBODs info from Oneview
        """
        super().__init__(self.SCHEMA_NAME)

        drive_technologies = \
            server_hardware_type['storageCapabilities']['driveTechnologies']

        self.redfish["@odata.id"] = \
            ComputerSystem.BASE_URI + "/" \
            + server_profile["uuid"] + "/Storage/1"
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Storage.Storage"
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["StorageControllers@odata.count"] = 1
        self.redfish["Id"] = "1"
        self.redfish["Name"] = "Storage Controller"
        self.redfish["Status"] = collections.OrderedDict()
        ok_struct = status_mapping.STATUS_MAP.get("OK")
        self.redfish["Status"]["State"] = ok_struct["State"]
        self.redfish["Status"]["Health"] = ok_struct["Health"]
        self.redfish["StorageControllers"] = list()

        # adapter storage capabilities (if any)
        for adapter in server_hardware_type['adapters']:
            if adapter['storageCapabilities']:
                new_capability = collections.OrderedDict()
                new_capability["SupportedDeviceProtocols"] = sorted(
                    self.map_supported_device_protos(drive_technologies))
                self.redfish["StorageControllers"].append(new_capability)

        # internal storage capabilities
        storage_controllers = collections.OrderedDict()
        storage_controllers["Manufacturer"] = "HPE"
        storage_controllers["SupportedDeviceProtocols"] = \
            sorted(self.map_supported_device_protos(drive_technologies))
        self.redfish["StorageControllers"].append(storage_controllers)

        count_drives_by_jbod = \
            [int(item["numPhysicalDrives"]) for item in sas_logical_jbods]

        count_drives = reduce(operator.add, count_drives_by_jbod, 0)

        self.redfish["Drives@odata.count"] = count_drives
        self.redfish["Drives"] = list()
        for i in range(count_drives):
            drive_id = str(i + 1)
            self.redfish["Drives"].append({
                "@odata.id": self.redfish["@odata.id"] + "/Drives/" + drive_id
            })

        self._validate()

    def map_supported_device_protos(self, drive_technologies):
        supported_device_protocols = set()

        try:
            for drive_option in drive_technologies:
                supported_device_protocols.add(
                    DEVICE_PROTOCOLS_MAP[drive_option])
        except Exception:
            supported_device_protocols.add('')

        return supported_device_protocols
