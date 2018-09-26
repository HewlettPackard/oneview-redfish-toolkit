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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class NetworkDeviceFunctionCollection(RedfishJsonValidator):
    """Creates a Network Device Function Collection Redfish dict

        Populates self.redfish with a NetworkDeviceFunctionCollection
    """

    SCHEMA_NAME = 'NetworkDeviceFunctionCollection'

    def __init__(self, device_id, server_hardware):
        """NetworkDeviceFunctionCollection constructor

            Populates self.redfish and calls _validate()

            Args:
                server_hardware: a server hardware dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Network Device Function Collection"
        members_count = 0
        self.redfish["Members"] = list()

        physical_ports = self.get_resource_by_id(
            server_hardware["portMap"]["deviceSlots"], "deviceNumber",
            device_id)["physicalPorts"]

        for port in physical_ports:
            physical_port = str(port["portNumber"])
            for virtual_port in port["virtualPorts"]:
                virtual_port_id = "_".join((
                    physical_port,
                    str(virtual_port["portNumber"]),
                    virtual_port["portFunction"]))
                members_count += 1
                device_link = dict()
                device_link["@odata.id"] = \
                    "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
                    "/NetworkAdapters/" + device_id + \
                    "/NetworkDeviceFunctions/" + virtual_port_id
                self.redfish["Members"].append(device_link)
        self.redfish["Members@odata.count"] = members_count
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkDeviceFunctionCollection" \
            ".NetworkDeviceFunctionCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/" + \
            server_hardware["uuid"] + "/NetworkAdapters/" + device_id + \
            "/NetworkDeviceFunctions/"

        self._validate()
