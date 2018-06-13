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

from oneview_redfish_toolkit.api.resource_block import ResourceBlock

STATE_TO_STATUS_MAPPING = {
    "NoProfileApplied": "Unused",
    "ApplyingProfile": "Composing",
    "ProfileApplied": "Composed",
    "ProfileError": "Failed"
}


class ServerHardwareResourceBlock(ResourceBlock):
    """Creates a ResourceBlock Redfish dict for Server Hardware

        Populates self.redfish with some hardcoded ResourceBlock
        values and with Server Hardware data retrieved from OneView.
    """

    def __init__(self, uuid, server_hardware, server_profile_templates):
        """ServerHardwareResourceBlock constructor

            Populates self.redfish with the contents of ServerHardware dict.

            Args:
                uuid: server hardware UUID
                server_hardware: ServerHardware dict from OneView
                server_profile_templates: list of OneView server profile
                templates
        """
        super().__init__(uuid, server_hardware)

        self.server_hardware = server_hardware
        self.server_profile_templates = server_profile_templates

        self.redfish["ResourceBlockType"] = ["ComputerSystem"]

        self.redfish["CompositionStatus"]["SharingCapable"] = False
        self.redfish["CompositionStatus"]["CompositionState"] = \
            self.get_composition_state()

        self.fill_memory()
        self.fill_processors()
        self.fill_links()

        self._validate()

    def get_composition_state(self):
        sh_state = self.server_hardware["state"]

        return STATE_TO_STATUS_MAPPING.get(sh_state, None)

    def fill_memory(self):
        self.redfish["Memory"] = list()

        memory = dict()
        memory["@odata.id"] = "/redfish/v1/CompositionService/" \
            "ResourceBlocks/{}/Memory/1".format(self.uuid)

        self.redfish["Memory"].append(memory)
        self.redfish["Memory@odata.count"] = len(self.redfish["Memory"])

    def fill_processors(self):
        processor_count = self.server_hardware["processorCount"]

        self.redfish["Processors@odata.count"] = processor_count
        self.redfish["Processors"] = list()

        for id in range(processor_count):
            processor = dict()

            processor["@odata.id"] = "/redfish/v1/CompositionService/" \
                "ResourceBlocks/{}/Processors/{}".format(self.uuid, (id + 1))

            self.redfish["Processors"].append(processor)

    def fill_links(self):
        self.redfish["Links"] = dict()

        chassi = dict()
        chassi["@odata.id"] = "/redfish/v1/Chassis/" + self.uuid
        self.redfish["Links"]["Chassis"] = list()
        self.redfish["Links"]["Chassis"].append(chassi)

        # TODO(svoboda) Check which computer system should be included
        # (server profile or server hardware).
        if self.server_hardware["serverProfileUri"]:
            sp_id = self.server_hardware["serverProfileUri"].split("/")[-1]

            system = dict()
            system["@odata.id"] = "/redfish/v1/Systems/" + sp_id
            self.redfish["Links"]["ComputerSystems"] = list()
            self.redfish["Links"]["ComputerSystems"].append(system)

        if self.server_profile_templates:
            self.redfish["Links"]["Zones"] = list()

            for spt in self.server_profile_templates:
                spt_id = spt["uri"].split("/")[-1]

                zone = dict()
                zone["@odata.id"] = \
                    "/redfish/v1/CompositionService/ResourceZones/" + spt_id

                self.redfish["Links"]["Zones"].append(zone)
