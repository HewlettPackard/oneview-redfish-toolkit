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


class NetworkInterface(RedfishJsonValidator):
    """Creates a NetworkInterface Redfish dict

        Populates self.redfish with NetworkInterface data retrieved from
        OneView
    """

    SCHEMA_NAME = 'NetworkInterface'

    def __init__(self, device_id, server_profile, server_hardware):
        """NetworkInterface constructor

            Populates self.redfish with the contents of server hardware dict
            from Oneview

            Args:
                device_id: The Network Interface ID
                server_profile: Oneview's server profile dict
                server_hardware: Oneview's server hardware dict
        """
        super().__init__(self.SCHEMA_NAME)
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = device_id

        self.redfish["Name"] = self.get_resource_by_id(
            server_hardware["portMap"]["deviceSlots"], "deviceNumber",
            device_id)["deviceName"]

        self.redfish["Links"] = dict()
        self.redfish["Links"]["NetworkAdapter"] = dict()
        self.redfish["Links"]["NetworkAdapter"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id

        self.redfish["NetworkPorts"] = dict()
        self.redfish["NetworkPorts"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + "/NetworkPorts/"

        self.redfish["NetworkDeviceFunctions"] = dict()
        self.redfish["NetworkDeviceFunctions"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
            "/NetworkAdapters/" + device_id + "/NetworkDeviceFunctions/"

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkInterface.NetworkInterface"
        self.redfish["@odata.id"] = "/redfish/v1/Systems/" + \
            server_profile["uuid"] + "/NetworkInterfaces/" + device_id

        self._validate()
