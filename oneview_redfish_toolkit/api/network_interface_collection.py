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


class NetworkInterfaceCollection(RedfishJsonValidator):
    """Creates a Network Interface Collection Redfish dict

        Populates self.redfish with some hardcoded NetworkInterfaceCollection
        values and Oneview ServerHardware result
    """

    SCHEMA_NAME = 'NetworkInterfaceCollection'

    def __init__(self, server_profile, server_hardware):
        """NetworkInterfaceCollection constructor

            Populates self.redfish and calls _validate()

            Args:
                server_profile: a server profile dict from OneView
                server_hardware: a server hardware dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Network Interface Collection"
        members_count = 0
        self.redfish["Members"] = list()
        for device in server_hardware["portMap"]["deviceSlots"]:
            for port in device["physicalPorts"]:
                if port["type"] in ["Ethernet", "FibreChannel", "InfiniBand"]:
                    members_count += 1
                    device_link = dict()
                    device_link["@odata.id"] = \
                        "/redfish/v1/Systems/" + server_profile["uuid"] + \
                        "/NetworkInterfaces/" + str(device["deviceNumber"])
                    self.redfish["Members"].append(device_link)
                    break
        self.redfish["Members@odata.count"] = members_count
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkInterfaceCollection" \
            ".NetworkInterfaceCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Systems/" + \
            server_profile["uuid"] + "/NetworkInterfaces"

        self._validate()
