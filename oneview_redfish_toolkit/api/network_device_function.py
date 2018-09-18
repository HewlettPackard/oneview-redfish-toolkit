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
from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class NetworkDeviceFunction(RedfishJsonValidator):
    """Creates a NetworkDeviceFunction Redfish dict

        Populates self.redfish with NetworkDeviceFunction data retrieved from
        OneView
    """

    SCHEMA_NAME = 'NetworkDeviceFunction'

    def __init__(self, device_id, device_function_id, server_hardware):
        """NetworkDeviceFunction constructor

            Populates self.redfish with the contents of server hardware dict
            from Oneview

            Args:
                device_id: ID of the NetworkAdapter
                device_function_id: ID of the DeviceFunction. Expected format:
                    portNumber_virtualPortNumber_virtualPortFunction
                server_hardware: Oneview's server hardware dict
        """
        super().__init__(self.SCHEMA_NAME)

        # device_function_id validation
        try:
            port_number, virtual_port_number, virtual_port_function = \
                device_function_id.split("_")

            physical_ports = self.get_resource_by_id(
                server_hardware["portMap"]["deviceSlots"], "deviceNumber",
                device_id)["physicalPorts"]

            port = self.get_resource_by_id(
                physical_ports, "portNumber", port_number)

            virtual_port = self.get_resource_by_id(
                port["virtualPorts"], "portNumber", virtual_port_number)
        except Exception:
            raise OneViewRedfishResourceNotFoundError(
                device_function_id, "NetworkDeviceFunction")

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = device_function_id
        self.redfish["Name"] = "Physical port {}, virtual port {}, device "\
            "function {}".format(
                port_number, virtual_port_number, virtual_port_function)

        if port["type"] == "Ethernet":
            self.redfish["Ethernet"] = dict()
            self.redfish["Ethernet"]["MACAddress"] = virtual_port["mac"]
            self.redfish["NetDevFuncType"] = "Ethernet"
        elif port["type"] == "FibreChannel":
            raise OneViewRedfishError("FibreChannel not implemented")
        else:
            raise OneViewRedfishError("Type not supported")

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkDeviceFunction.NetworkDeviceFunction"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/" + \
            server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + \
            "/NetworkDeviceFunctions/" + device_function_id

        self._validate()
