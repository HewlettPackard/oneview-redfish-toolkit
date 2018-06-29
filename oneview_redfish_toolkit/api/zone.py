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
from oneview_redfish_toolkit.api.zone_collection import ZoneCollection


class Zone(RedfishJsonValidator):
    """Creates a Zone Redfish dict

        Populates self.redfish with Zone data retrieved from
        OneView
    """

    SCHEMA_NAME = 'Zone'

    def __init__(self, profile_template, available_targets_obj, drives):
        """Zone constructor

            Populates self.redfish with the contents of
            server profile template and available targets dict from Oneview

            Args:
                profile_template: Oneview's server profile template dict
                available_targets_obj: Oneview's available targets dict
                (servers and empty bays) for assignment to a server profile
        """
        super().__init__(self.SCHEMA_NAME)

        self.available_targets = available_targets_obj["targets"]
        self.drives = []

        controllers = profile_template["localStorage"]["controllers"]
        has_not_embedded = \
            [i for i in controllers if i["deviceSlot"] != "Embedded"]

        if has_not_embedded:
            self.drives = drives

        self.redfish["@odata.type"] = "#Zone.v1_1_0.Zone"
        self.redfish["Id"] = profile_template["uri"].split("/")[-1]
        self.redfish["Name"] = profile_template["name"]
        status_from_ov = profile_template["status"]
        self.redfish["Status"] = status_mapping.STATUS_MAP[status_from_ov]

        self.redfish["Links"] = dict()
        self.redfish["Links"]["ResourceBlocks"] = list()

        self.fill_resource_blocks()

        self.capabilities_key = "@Redfish.CollectionCapabilities"
        self.redfish[self.capabilities_key] = dict()
        self.redfish[self.capabilities_key]["@odata.type"] = \
            "#CollectionCapabilities.v1_0_0.CollectionCapabilities"
        self.redfish[self.capabilities_key]["Capabilities"] = list()

        self.fill_capabilities_collection()

        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Zone.Zone"
        self.redfish["@odata.id"] = ZoneCollection.BASE_URI + "/" +\
            self.redfish["Id"]

        self._validate()

    def fill_resource_blocks(self):
        for item in self.available_targets:
            self.add_resource_block_item_to_links(item, "serverHardwareUri")

        for item in self.drives:
            self.add_resource_block_item_to_links(item, "uri")

    def add_resource_block_item_to_links(self, original_dict, uri_key):
        uuid = original_dict[uri_key].split("/")[-1]
        dict_item = dict()
        dict_item["@odata.id"] = ResourceBlockCollection.BASE_URI + "/" + uuid
        self.redfish["Links"]["ResourceBlocks"].append(dict_item)

    def fill_capabilities_collection(self):
        capability = {
            "CapabilitiesObject": {
                "@odata.id": "/redfish/v1/Systems/Capabilities/" +
                             self.redfish["Id"]
                # TODO(@ricardogpsf) When the Capabilities API is created,
                # replace the URI string with a constant
            },
            "UseCase": "ComputerSystemComposition",
            "Links": {
                "TargetCollection": {
                    "@odata.id": ComputerSystem.BASE_URI
                }
            }
        }
        self.redfish[self.capabilities_key]["Capabilities"].append(capability)
