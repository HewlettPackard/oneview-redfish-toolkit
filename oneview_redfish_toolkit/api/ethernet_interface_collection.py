# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class EthernetInterfaceCollection(RedfishJsonValidator):
    """Creates a Ethernet Interface Collection Redfish dict

        Populates self.redfish with some hardcoded EthernetInterfaceCollection
        values and Oneview Server Profile information
    """

    SCHEMA_NAME = 'EthernetInterfaceCollection'

    def __init__(self, server_profile):
        """EthernetInterfaceCollection constructor

            Populates self.redfish and calls _validate()

            Args:
                server_profile: a server profile dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        odata_uri = ComputerSystem.BASE_URI + "/" + \
            server_profile["uuid"] + "/EthernetInterfaces"

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Ethernet Interface Collection"

        connections = server_profile["connectionSettings"]["connections"]
        ethernet_list = []
        for conn in connections:
            if conn["functionType"] == "Ethernet":
                item_redfish = {"@odata.id": odata_uri + "/" + str(conn["id"])}
                ethernet_list.append(item_redfish)

        self.redfish["Members@odata.count"] = len(ethernet_list)
        self.redfish["Members"] = ethernet_list
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EthernetInterfaceCollection." \
            "EthernetInterfaceCollection"
        self.redfish["@odata.id"] = odata_uri

        self._validate()
