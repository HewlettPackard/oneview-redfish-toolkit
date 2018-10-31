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
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection
from oneview_redfish_toolkit.api import status_mapping


class EthernetInterface(RedfishJsonValidator):
    """Creates a Ethernet Interface Redfish dict

        Populates self.redfish with some hardcoded EthernetInterface
        values and Oneview's Server Profile, Connection and Network
    """

    SCHEMA_NAME = 'EthernetInterface'
    METADATA_INFO = "/redfish/v1/$metadata#EthernetInterface.EthernetInterface"

    def __init__(self, data):
        """EthernetInterfaceCollection constructor

            Populates self.redfish and calls _validate()

            Args:
                server_profile: a server profile dict from OneView
                connection: a connection dict from server profile
                network_attr: a network (or networkSet) dict from
                OneView index resources
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()

        self.redfish.update(data)

        self.redfish["@odata.context"] = self.__class__.METADATA_INFO

        self._validate()

    @staticmethod
    def build(server_profile, connection, network_attr):
        conn_id = str(connection["id"])
        odata_uri = ComputerSystem.BASE_URI + "/" \
            + server_profile["uuid"] + "/EthernetInterfaces/" + conn_id
        attrs = {
            "Id": conn_id,
            "Name": connection["name"],
            "Status": status_mapping.STATUS_MAP[connection["status"]],
            "MACAddress": connection["mac"],
            "SpeedMbps": int(connection["allocatedMbps"])
        }
        if connection["macType"] == "Physical":
            attrs["PermanentMACAddress"] = connection["mac"]

        EthernetInterface._fill_vlan_info(attrs, network_attr, odata_uri)

        attrs["@odata.id"] = odata_uri

        return EthernetInterface(attrs)

    @staticmethod
    def build_resource_block(server_profile_template, connection, network):
        conn_id = str(connection["id"])
        server_profile_template_id = \
            server_profile_template["uri"].split("/")[-1]
        odata_id = ResourceBlockCollection.BASE_URI + "/" \
            + server_profile_template_id \
            + "/EthernetInterfaces/" \
            + conn_id

        attrs = {
            "Id": conn_id,
            "Name": network["name"],
            "SpeedMbps": int(connection["requestedMbps"])
        }

        EthernetInterface._fill_vlan_info(attrs, network, odata_id)

        attrs["@odata.id"] = odata_id

        return EthernetInterface(attrs)

    @staticmethod
    def _fill_vlan_info(attrs_dict, network_attr, base_odata_uri):
        if network_attr["category"] == "network-sets":
            attrs_dict["VLANs"] = {"@odata.id": base_odata_uri + "/VLANs"}
        else:
            attrs_dict["VLAN"] = dict()
            attrs_dict["VLAN"]["VLANEnable"] = True
            attrs_dict["VLAN"]["VLANId"] = \
                int(network_attr["attributes"]["vlan_id"])
