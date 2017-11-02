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
                    portNumber_virtualPortNumber_virutalPortFunction
                server_hardware: Oneview's server hardware dict
        """
        super().__init__(self.SCHEMA_NAME)
        index = int(device_id) - 1
        # device_function_id validation
        try:
            port_Number, vitualPortNumber, virtualPortFuncion = \
                device_function_id.split("_")
            port_index = int(port_Number) - 1
            virtual_port_index = int(vitualPortNumber) - 1
            virtual_port_function_validation = server_hardware["portMap"][
                "deviceSlots"][index]["physicalPorts"][port_index][
                "virtualPorts"][virtual_port_index]["portFunction"]
        except Exception:
            raise OneViewRedfishResourceNotFoundError(
                device_function_id, "NetworkDeviceFunction")

        if virtual_port_function_validation != virtualPortFuncion:
            raise OneViewRedfishResourceNotFoundError(
                device_function_id, "NetworkDeviceFunction")

        self.redfish["@odata.type"] = \
            "#NetworkDeviceFunction.v1_1_0.NetworkDeviceFunction"
        self.redfish["Id"] = device_function_id
        self.redfish["Name"] = "Physical port {}, virtual port {}, device "\
            "function {}".format(
                port_Number, vitualPortNumber, virtualPortFuncion)

        port = server_hardware["portMap"]["deviceSlots"][index][
            "physicalPorts"][port_index]

        if port["type"] == "Ethernet":
            virtual_port = server_hardware["portMap"]["deviceSlots"][index][
                "physicalPorts"][port_index]["virtualPorts"][
                virtual_port_index]
            self.redfish["Ethernet"] = dict()
            self.redfish["Ethernet"]["MACAddress"] = virtual_port["mac"]
        elif port["type"] == "FibreChannel":
            self.redfish["NetDevFuncType"] = "FibreChannel"
            self.redfish["FibreChannel"] = 
        else:
            raise OneViewRedfishError("Type not supported")

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkDeviceFunction.NetworkDeviceFunction"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/" + \
            server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + \
            "/NetworkDeviceFunctions/" + device_function_id
        self._validate()
