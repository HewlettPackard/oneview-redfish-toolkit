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
from oneview_redfish_toolkit.api import status_mapping


class EthernetInterface(RedfishJsonValidator):
    """Creates a Ethernet Interface Redfish dict

        Populates self.redfish with some hardcoded EthernetInterface
        values and Oneview's Server Profile, Connection and Network
    """

    SCHEMA_NAME = 'EthernetInterface'

    def __init__(self, server_profile, connection, network_attr):
        """EthernetInterfaceCollection constructor

            Populates self.redfish and calls _validate()

            Args:
                server_profile: a server profile dict from OneView
                connection: a connection dict from server profile
                network_attr: a network (or networkSet) dict from
                OneView index resources
        """
        super().__init__(self.SCHEMA_NAME)

        conn_id = str(connection["id"])
        odata_uri = ComputerSystem.BASE_URI + "/" \
            + server_profile["uuid"] + "/EthernetInterfaces/" + conn_id

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = conn_id
        self.redfish["Name"] = connection["name"]
        self.redfish["Status"] = status_mapping \
            .STATUS_MAP[connection["status"]]

        self.redfish["MACAddress"] = connection["mac"]
        if connection["macType"] == "Physical":
            self.redfish["PermanentMACAddress"] = connection["mac"]

        self.redfish["SpeedMbps"] = int(connection["allocatedMbps"])

        if network_attr["category"] == "network-sets":
            self.redfish["VLANs"] = {"@odata.id": odata_uri + "/VLANs"}
        else:
            self.redfish["VLAN"] = dict()
            self.redfish["VLAN"]["VLANEnable"] = True
            self.redfish["VLAN"]["VLANId"] = \
                int(network_attr["attributes"]["vlan_id"])

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EthernetInterface.EthernetInterface"
        self.redfish["@odata.id"] = odata_uri

        self._validate()
