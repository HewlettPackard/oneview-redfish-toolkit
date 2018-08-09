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

    def __init__(self,
                 sh_with_profile_applied,
                 server_profile_templates,
                 zone_ids):
        """ComputerSystemCollection constructor

            Populates self.redfish with a hardcoded ComputerSystemCollection
            values and with the response of Oneview with all servers with
            Server Profile applied and all server profile templates.

            Args:
                sh_with_profile_applied: A list of dicts of server hardware
                    with profile applied.
                server_profile_templates: A list of dicts of server profile
                    templates
                zone_ids: A list of Zone Ids
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Computer System Collection"
        server_profile_members_list = \
            self._get_server_profile_members_list(sh_with_profile_applied)
        self.redfish["Members@odata.count"] = \
            len(server_profile_members_list)
        self.redfish["Members"] = server_profile_members_list

        self._set_collection_capabilities(server_profile_templates, zone_ids)

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
                list: list of computer system members to be filled on
                Redfish Members.
        """
        members = list()
        for server_hardware in server_hardware_list:
            server_profile_uuid = \
                server_hardware["serverProfileUri"].split("/")[-1]
            members.append({
                "@odata.id": "/redfish/v1/Systems/" + server_profile_uuid
            })

        return members

    def _set_collection_capabilities(self, server_profile_templates, zone_ids):
        self.capabilities_key = "@Redfish.CollectionCapabilities"
        self.redfish[self.capabilities_key] = dict()
        self.redfish[self.capabilities_key]["@odata.type"] = \
            self.get_odata_type_by_schema('CollectionCapabilities')
        self.redfish[self.capabilities_key]["Capabilities"] = list()

        for server_profile_template in server_profile_templates:
            spt_id = server_profile_template["uri"].split("/")[-1]

            capability = self._get_capability_object(spt_id, zone_ids)

            self.redfish[self.capabilities_key]["Capabilities"].\
                append(capability)

    def _get_capability_object(self, spt_id, zone_ids):
        capability = OrderedDict()
        capability["CapabilitiesObject"] = dict()
        capability["CapabilitiesObject"]["@odata.id"] = \
            ComputerSystem.BASE_URI + "/" + spt_id
        capability["UseCase"] = "ComputerSystemComposition"
        capability["Links"] = dict()
        capability["Links"]["TargetCollection"] = dict()
        capability["Links"]["TargetCollection"]["@odata.id"] = \
            ComputerSystem.BASE_URI

        zone_ids_filtered = filter(lambda zone_id: spt_id in zone_id, zone_ids)
        self._build_capability_related_items(capability, zone_ids_filtered)

        return capability

    def _build_capability_related_items(self,
                                        capability,
                                        zone_ids_of_capability):
        capability["Links"]["RelatedItem"] = list()
        for zone_id in zone_ids_of_capability:
            related_item = dict()
            related_item["@odata.id"] = ZoneCollection.BASE_URI + "/" + zone_id
            capability["Links"]["RelatedItem"].append(related_item)
