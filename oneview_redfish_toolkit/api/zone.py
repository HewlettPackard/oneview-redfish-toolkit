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


class Zone(RedfishJsonValidator):
    """Creates a Zone Redfish dict

        Populates self.redfish with Zone data retrieved from
        OneView
    """

    SCHEMA_NAME = 'Zone'

    def __init__(self, profile_template, enclosure_group_resource, drives=[]):
        """Zone constructor

            Populates self.redfish with the contents of
            server profile template and server hardware list from Oneview

            Args:
                profile_template: Oneview's server profile template dict
                enclosure_group_resource: Oneview's enclosure group index trees
                (servers and empty bays) for assignment to a server profile
                drives: Oneview's dict drives list
        """
        super().__init__(self.SCHEMA_NAME)

        has_valid_controller = \
            ComputerSystem.get_storage_controller(profile_template)

        if not has_valid_controller:
            drives = []

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = profile_template["uri"].split("/")[-1]
        self.redfish["Name"] = profile_template["name"]
        status_from_ov = profile_template["status"]
        self.redfish["Status"] = status_mapping.STATUS_MAP[status_from_ov]

        self.redfish["Links"] = dict()
        self.redfish["Links"]["ResourceBlocks"] = list()

        self.fill_resource_blocks(profile_template, enclosure_group_resource,
                                  drives)

        self.capabilities_key = "@Redfish.CollectionCapabilities"
        self.redfish[self.capabilities_key] = dict()
        self.redfish[self.capabilities_key]["@odata.type"] = \
            self.get_odata_type_by_schema('CollectionCapabilities')
        self.redfish[self.capabilities_key]["Capabilities"] = list()

        self.fill_capabilities_collection()

        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Zone.Zone"
        self.redfish["@odata.id"] = ZoneCollection.BASE_URI + "/" +\
            self.redfish["Id"]

        self._validate()

    def fill_resource_blocks(self, profile_template, enclosure_group_resource,
                             drives):
        server_hardware_list = \
            self._get_server_hardware_list(enclosure_group_resource)

        for item in server_hardware_list:
            self.add_resource_block_item_to_links(item, "uri")

        for item in drives:
            self.add_resource_block_item_to_links(item, "uri")

        self._fill_network_resource_block(profile_template)

    def _get_server_hardware_list(self, encl_group):
        server_hardware_list = list()
        logical_encl = \
            encl_group["children"]["ENCLOSURE_GROUP_TO_LOGICAL_ENCLOSURE"][0]
        enclosures = logical_encl["children"]["LOGICAL_ENCLOSURE_TO_ENCLOSURE"]

        for enclosure in enclosures:
            device_uris = \
                enclosure["resource"]["multiAttributes"]["device_uri"]
            server_hardware_uris = self._get_server_hardware_uris(device_uris)
            server_hardware_list.extend(server_hardware_uris)

        return server_hardware_list

    @staticmethod
    def _get_server_hardware_uris(device_uris):
        server_hardware_uris = list()
        for uri in filter(None, device_uris):
            if "server-hardware" in uri:
                server_hardware_uris.append({"uri": uri})

        return server_hardware_uris

    def add_resource_block_item_to_links(self, original_dict, uri_key):
        uuid = original_dict[uri_key].split("/")[-1]
        dict_item = dict()
        dict_item["@odata.id"] = ResourceBlockCollection.BASE_URI + "/" + uuid
        self.redfish["Links"]["ResourceBlocks"].append(dict_item)

    def _fill_network_resource_block(self, profile_template):
        conn_settings = profile_template["connectionSettings"]

        if conn_settings["connections"]:
            self.add_resource_block_item_to_links(profile_template, "uri")

    def fill_capabilities_collection(self):
        capability = {
            "CapabilitiesObject": {
                "@odata.id":
                    CapabilitiesObject.BASE_URI + "/" + self.redfish["Id"]
            },
            "UseCase": "ComputerSystemComposition",
            "Links": {
                "TargetCollection": {
                    "@odata.id": ComputerSystem.BASE_URI
                }
            }
        }
        self.redfish[self.capabilities_key]["Capabilities"].append(capability)
