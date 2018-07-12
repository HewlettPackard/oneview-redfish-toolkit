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

from collections import OrderedDict

from oneview_redfish_toolkit.api.computer_system \
    import ComputerSystem
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.zone_collection \
    import ZoneCollection


class ComputerSystemCollection(RedfishJsonValidator):
    """Creates a Computer System Collection Redfish dict

        Populates self.redfish with some hardcoded ComputerSystemCollection
        values and with the response of Oneview with all servers with
        Server Profile applied.
    """

    SCHEMA_NAME = 'ComputerSystemCollection'

    def __init__(self, server_hardware_list, server_profile_templates):
        """ComputerSystemCollection constructor

            Populates self.redfish with a hardcoded ComputerSystemCollection
            values and with the response of Oneview with all servers with
            Server Profile applied.

            Args:
                server_hardware: A list of dicts of server hardware.
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = \
            "#ComputerSystemCollection.ComputerSystemCollection"
        self.redfish["Name"] = "Computer System Collection"
        server_profile_members_list = \
            self._get_server_profile_members_list(server_hardware_list)
        self.redfish["Members@odata.count"] = \
            len(server_profile_members_list)
        self.redfish["Members"] = server_profile_members_list

        self._set_collection_capabilities(server_profile_templates)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ComputerSystemCollection" \
            ".ComputerSystemCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Systems"

        self._validate()

    def _get_server_profile_members_list(self, server_hardware_list):
        """Returns a redfish members list with all server profiles applied

            Iterate over the server hardware list, filter the
            UUIDs of server profiles that are applied and mounts
            the member item to be filled on Redfish Members.

            Args:
                server_hardware_list: list of Oneview's server
                hardwares information.

            Returns:
                list: list of Server Profile applied to be filled on
                Redfish Members.
        """
        server_profile_members_list = list()
        for server_hardware in server_hardware_list:
            if server_hardware["state"] == "ProfileApplied":
                server_profile_uuid = \
                    server_hardware["serverProfileUri"].split("/")[-1]
                server_profile_members_list.append({
                    "@odata.id": "/redfish/v1/Systems/" + server_profile_uuid
                })

        return server_profile_members_list

    def _set_collection_capabilities(self, server_profile_templates):
        self.capabilities_key = "@Redfish.CollectionCapabilities"
        self.redfish[self.capabilities_key] = dict()
        self.redfish[self.capabilities_key]["@odata.type"] = \
            "#CollectionCapabilities.v1_0_0.CollectionCapabilities"
        self.redfish[self.capabilities_key]["Capabilities"] = list()

        for server_profile_template in server_profile_templates:
            zone_id = server_profile_template["uri"].split("/")[-1]

            capability = self._get_capability_object(zone_id)

            self.redfish[self.capabilities_key]["Capabilities"].\
                append(capability)

    def _get_capability_object(self, zone_id):
        capability = OrderedDict()
        capability["CapabilitiesObject"] = dict()
        capability["CapabilitiesObject"]["@odata.id"] = \
            ComputerSystem.BASE_URI + "/" + zone_id
        capability["UseCase"] = "ComputerSystemComposition"
        capability["Links"] = dict()
        capability["Links"]["TargetCollection"] = dict()
        capability["Links"]["TargetCollection"]["@odata.id"] = \
            ComputerSystem.BASE_URI
        capability["Links"]["RelatedItem"] = list()
        related_item = dict()
        related_item["@odata.id"] = ZoneCollection.BASE_URI + "/" + zone_id
        capability["Links"]["RelatedItem"].append(related_item)

        return capability
