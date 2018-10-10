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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class NetworkAdapter(RedfishJsonValidator):
    """Creates a NetworkAdapter Redfish dict

        Populates self.redfish with NetworkAdapter data retrieved from
        OneView
    """

    SCHEMA_NAME = 'NetworkAdapter'

    def __init__(self, device_id, server_hardware):
        """NetworkAdapter constructor

            Populates self.redfish with the contents of server hardware dict
            from Oneview

            Args:
                device_id: The id of the Network Adapter in OneView dict
                server_hardware: Oneview's server hardware dict
        """
        super().__init__(self.SCHEMA_NAME)
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = device_id

        device_slot = self.get_resource_by_id(
            server_hardware["portMap"]["deviceSlots"],
            "deviceNumber", device_id)

        self.redfish["Name"] = device_slot["deviceName"]

        self.redfish["Controllers"] = list()
        self.redfish["Controllers"].append(collections.OrderedDict())

        # ControllerCapabilities property
        self.redfish["Controllers"][0]["ControllerCapabilities"] = \
            collections.OrderedDict()
        port_count = len(device_slot["physicalPorts"])
        virtual_port_count = 0
        if port_count > 0:
            for i in range(0, port_count):
                virtual_port_count += len(
                    device_slot["physicalPorts"][i]["virtualPorts"])
        self.redfish["Controllers"][0]["ControllerCapabilities"][
            "NetworkPortCount"] = port_count
        self.redfish["Controllers"][0]["ControllerCapabilities"][
            "NetworkDeviceFunctionCount"] = virtual_port_count

        # Removing Links property (since it is causing validation error)
        # and this info is available in the NetworkPorts and
        # NetworkDeviceFunctions links below
        # # Links property
        # self.redfish["Controllers"][0]["Links"] = collections.OrderedDict()
        # self.redfish["Controllers"][0]["Links"]["NetworkPorts"] = list()
        # self.redfish["Controllers"][0]["Links"]["NetworkDeviceFunctions"] = \
        #     list()

        # # Adding NetworkPorts
        # for port in device_slot["physicalPorts"]:
        #     new_port = {
        #         "@odata:id": "/redfish/v1/Chassis/" +
        #         server_hardware["uuid"] +
        #         "/NetworkAdapters/" + device_id + "/NetworkPorts/" +
        #         str(port["portNumber"])}
        #     self.redfish["Controllers"][0]["Links"]["NetworkPorts"].\
        #         append(new_port)

        #     # Adding NetworkDeviceFunction
        #     for virtual_port in port["virtualPorts"]:
        #         network_device_function_id = "_".join((
        #             str(port["portNumber"]),
        #             str(virtual_port["portNumber"]),
        #             virtual_port["portFunction"]))
        #         network_device_function = {
        #             "@odata:id": "/redfish/v1/Chassis/" +
        #             server_hardware["uuid"] + "/NetworkAdapters/" +
        #             device_id + "/NetworkDeviceFunctions/" +
        #             network_device_function_id}
        #         self.redfish["Controllers"][0]["Links"][
        #             "NetworkDeviceFunctions"].append(network_device_function)
        self.redfish["NetworkPorts"] = dict()
        self.redfish["NetworkPorts"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + "/NetworkPorts/"

        self.redfish["NetworkDeviceFunctions"] = dict()
        self.redfish["NetworkDeviceFunctions"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + "/NetworkDeviceFunctions/"

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkAdapter.NetworkAdapter"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/" + \
            server_hardware["uuid"] + "/NetworkAdapters/" + device_id

        self._validate()
