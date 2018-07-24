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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection


class ResourceBlockEthernetInterface(RedfishJsonValidator):
    """Creates a Ethernet Interface Redfish dict

        Populates self.redfish with ethernet interface data retrieved
        from OneView
    """

    SCHEMA_NAME = 'EthernetInterface'

    def __init__(self, server_profile_template, connection, network):
        """ResourceBlockEthernetInterface constructor

            Populates self.redfish with some hardcoded Resource Block
            values and with Server Profile Template and Ethernet Network
            data retrieved from OneView.

            Args:
                server_profile_template: Server Profile Template dict
                from OneView
                connection: Server Profile Template Connection dict
                from OneView
                network: Ethernet network dict from OneView
        """

        super().__init__(self.SCHEMA_NAME)

        server_profile_template_id = \
            server_profile_template["uri"].split("/")[-1]
        odata_id = ResourceBlockCollection.BASE_URI + "/" \
            + server_profile_template_id \
            + "/EthernetInterfaces/" \
            + str(connection["id"])

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = server_profile_template_id
        self.redfish["Name"] = network["name"]
        self.redfish["SpeedMbps"] = int(connection["requestedMbps"])

        if network["category"] == "ethernet-networks":
            self.redfish["VLAN"] = \
                self._create_vlan(network["attributes"]["vlan_id"])
        elif network["category"] == "network-sets":
            self.redfish["VLANs"] = dict()
            self.redfish["VLANs"]["@odata.id"] = \
                odata_id \
                + "/VLANs"

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EthernetInterface.EthernetInterface"
        self.redfish["@odata.id"] = odata_id

        self._validate()

    def _create_vlan(self, vlan_id):
        vlan = dict()
        vlan["VLANEnable"] = True
        vlan["VLANId"] = int(vlan_id)
        return vlan
