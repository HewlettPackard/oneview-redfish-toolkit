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

from oneview_redfish_toolkit.api.capabilities_object import \
    CapabilitiesObject
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection
from oneview_redfish_toolkit.api import status_mapping
from oneview_redfish_toolkit.api.zone_collection import ZoneCollection
from oneview_redfish_toolkit.services.computer_system_service import \
    ComputerSystemService


class Zone(RedfishJsonValidator):
    """Creates a Zone Redfish dict

        Populates self.redfish with Zone data retrieved from
        OneView
    """

    SCHEMA_NAME = 'Zone'

    def __init__(self,
                 resource_id,
                 profile_template,
                 server_hardware_list,
                 enclosure_name,
                 drives=[]):
        """Zone constructor

            Populates self.redfish with the contents of
            server profile template and server hardware list from Oneview

            Args:
                resource_id: The resource id
                profile_template: Oneview's server profile template dict
                server_hardware_list: Oneview's server hardware list
                (servers and empty bays) for assignment to a server profile
                enclosure_name: Enclosure name associated with a Zone.
                If Zone has not enclosure it will be None.
                drives: Oneview's dict drives list
        """
        super().__init__(self.SCHEMA_NAME)

        has_valid_controller = \
            ComputerSystemService.get_storage_controller(profile_template)

        if not has_valid_controller:
            drives = []

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = resource_id
        self.redfish["Name"] = self.get_zone_name(
            profile_template["name"], enclosure_name)
        status_from_ov = profile_template["status"]
        self.redfish["Status"] = status_mapping.STATUS_MAP[status_from_ov]

        self.redfish["Links"] = dict()
        self.redfish["Links"]["ResourceBlocks"] = list()

        self.fill_resource_blocks(profile_template, server_hardware_list,
                                  drives)

        self.capabilities_key = "@Redfish.CollectionCapabilities"
        self.redfish[self.capabilities_key] = dict()
        self.redfish[self.capabilities_key]["@odata.type"] = \
            self.get_odata_type_by_schema('CollectionCapabilities')
        self.redfish[self.capabilities_key]["Capabilities"] = list()

        self.fill_capabilities_collection(profile_template)

        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Zone.Zone"
        self.redfish["@odata.id"] = ZoneCollection.BASE_URI + "/" +\
            self.redfish["Id"]

        self._validate()

    @staticmethod
    def get_zone_name(spt_name, enclosure_name):
        zone_name = spt_name
        if enclosure_name:
            zone_name = spt_name + " - " + enclosure_name
        return zone_name

    def fill_resource_blocks(self, profile_template, server_hardware_list,
                             drives):
        for item in server_hardware_list:
            self.add_resource_block_item_to_links(item, "uri")

        for item in drives:
            self.add_resource_block_item_to_links(item, "uri")

        self.add_resource_block_item_to_links(profile_template, "uri")

    def add_resource_block_item_to_links(self, original_dict, uri_key):
        uuid = original_dict[uri_key].split("/")[-1]
        dict_item = dict()
        dict_item["@odata.id"] = ResourceBlockCollection.BASE_URI + "/" + uuid
        self.redfish["Links"]["ResourceBlocks"].append(dict_item)

    def fill_capabilities_collection(self, profile_template):
        spt_id = profile_template["uri"].split("/")[-1]
        capability = {
            "CapabilitiesObject": {
                "@odata.id":
                    CapabilitiesObject.BASE_URI + "/" + spt_id
            },
            "UseCase": "ComputerSystemComposition",
            "Links": {
                "TargetCollection": {
                    "@odata.id": ComputerSystem.BASE_URI
                }
            }
        }
        self.redfish[self.capabilities_key]["Capabilities"].append(capability)
