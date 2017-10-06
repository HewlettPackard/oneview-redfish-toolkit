# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Storage(RedfishJsonValidator):
    """Creates a Storage Redfish dict

        Populates self.redfish with Storage data retrieved from OneView
    """

    SCHEMA_NAME = 'Storage'

    def __init__(self, uuid, server_hardware_type):
        """Storage constructor

            Populates self.redfish with the contents of server hardware type

            Args:
                server_hardware_type: Server hardware type
        """
        super().__init__(self.SCHEMA_NAME)

        drive_technologies = \
            server_hardware_type['storageCapabilities']['driveTechnologies']

        self.redfish["@odata.id"] = \
            "/redfish/v1/Systems/" + uuid + "/Storage/1"
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Storage.Storage"
        self.redfish["@odata.type"] = "#Storage.v1_2_0.Storage"
        self.redfish["StorageControllers@odata.count"] = 1
        self.redfish["Id"] = "1"
        self.redfish["Name"] = "Storage Controller"
        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = "OK"
        self.redfish["StorageControllers"] = list()
        self.redfish["StorageControllers"].append(collections.OrderedDict())
        self.redfish["StorageControllers"][0]["Manufacturer"] = "HPE"
        self.redfish["StorageControllers"][0]["Model"] = "HPE Smart Array"
        self.redfish["StorageControllers"][0]["SupportedDeviceProtocols"] = \
            sorted(self.map_supported_device_protos(drive_technologies))

        self._validate()

    def map_supported_device_protos(self, drive_technologies):

        redfish_oneview_drive_technologies = dict()
        redfish_oneview_drive_technologies['SasHdd'] = 'SAS'
        redfish_oneview_drive_technologies['SasSsd'] = 'SAS'
        redfish_oneview_drive_technologies['SataHdd'] = 'SATA'
        redfish_oneview_drive_technologies['SataSsd'] = 'SATA'
        redfish_oneview_drive_technologies['NVMeHdd'] = 'NVMe'
        redfish_oneview_drive_technologies['NVMeSsd'] = 'NVMe'
        supported_device_protocols = set()

        try:
            for drive_option in drive_technologies:
                supported_device_protocols.add(
                    redfish_oneview_drive_technologies[drive_option])
        except Exception:
            supported_device_protocols.add('')

        return supported_device_protocols
