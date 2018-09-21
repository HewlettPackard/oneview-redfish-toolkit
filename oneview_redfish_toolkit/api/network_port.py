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

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class NetworkPort(RedfishJsonValidator):
    """Creates a NetworkPort Redfish dict

        Populates self.redfish with NetworkPort data retrieved from
        OneView
    """

    SCHEMA_NAME = 'NetworkPort'

    def __init__(self, device_id, port_id, server_hardware):
        """NetworkPort constructor

            Populates self.redfish with the contents of server hardware dict
            from Oneview

            Args:
                device_id: ID of the NetworkAdapter
                port_id: ID of the Port.
                server_hardware: Oneview's server hardware dict
        """
        super().__init__(self.SCHEMA_NAME)

        physical_ports = self.get_resource_by_id(
            server_hardware["portMap"]["deviceSlots"], "deviceNumber",
            device_id)["physicalPorts"]

        port = self.get_resource_by_id(physical_ports, "portNumber", port_id)

        if port["type"] not in ["Ethernet", "FibreChannel", "InfiniBand"]:
            raise OneViewRedfishError("Port ID refers to invalid port type.")

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = port_id
        self.redfish["Name"] = "Physical port {}".format(port_id)
        self.redfish["PhysicalPortNumber"] = port_id
        self.redfish["ActiveLinkTechnology"] = port["type"]
        self.redfish["AssociatedNetworkAddresses"] = list()
        if port["type"] == "Ethernet":
            self.redfish["AssociatedNetworkAddresses"].append(port["mac"])
        elif port["type"] == "FibreChannel":
            self.redfish["AssociatedNetworkAddresses"].append(port["wwn"])
        else:
            raise OneViewRedfishError("Type not supported")

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkPort.NetworkPort"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/" + \
            server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + \
            "/NetworkPorts/" + port_id

        self._validate()
