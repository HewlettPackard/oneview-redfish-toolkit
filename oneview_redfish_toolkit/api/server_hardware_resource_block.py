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
import collections
from oneview_redfish_toolkit.api.resource_block import ResourceBlock
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.services.zone_service import ZoneService

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

    def __init__(self, uuid, server_hardware, zone_ids):
        """ServerHardwareResourceBlock constructor

            Populates self.redfish with the contents of server hardware
            and server profile template dicts.

            Args:
                uuid: server hardware UUID
                server_hardware: ServerHardware dict from OneView
                zone_ids: list of Zone ids
        """
        super().__init__(uuid, server_hardware)

        self.server_hardware = server_hardware
        self.zone_ids = zone_ids

        self.redfish["ResourceBlockType"] = ["ComputerSystem"]

        self.redfish["CompositionStatus"]["SharingCapable"] = False

        composition_state = self._get_composition_state()
        self.redfish["CompositionStatus"]["CompositionState"] = \
            composition_state
        self.redfish["Status"] = collections.OrderedDict()
        state, health = status_mapping.\
            get_redfish_server_hardware_status_struct(server_hardware)
        self.redfish["Status"]["State"] = state
        self.redfish["Status"]["Health"] = health

        self._fill_computer_system()
        self._fill_links()

        self._validate()

    def _get_composition_state(self):
        composition_state = status_mapping.\
            get_redfish_composition_state(self.server_hardware)

        if not composition_state:
            composition_state = self._get_server_profile_state()

        return composition_state

    def _get_server_profile_state(self):
        server_profile_uri = self.server_hardware["serverProfileUri"]

        if server_profile_uri:
            return status_mapping.COMPOSITION_STATE["ProfileApplied"]
        else:
            return status_mapping.COMPOSITION_STATE["NoProfileApplied"]

    def _fill_computer_system(self):
        self.redfish["ComputerSystems"] = list()

        computer_system = dict()
        computer_system["@odata.id"] = \
            self.BASE_URI + "/" + self.uuid + "/Systems/1"

        self.redfish["ComputerSystems"].append(computer_system)

    def _fill_links(self):
        self.redfish["Links"] = dict()

        chassi = dict()
        chassi["@odata.id"] = "/redfish/v1/Chassis/" + self.uuid
        self.redfish["Links"]["Chassis"] = list()
        self.redfish["Links"]["Chassis"].append(chassi)

        if self.server_hardware["serverProfileUri"]:
            sp_id = self.server_hardware["serverProfileUri"].split("/")[-1]

            system = dict()
            system["@odata.id"] = "/redfish/v1/Systems/" + sp_id
            self.redfish["Links"]["ComputerSystems"] = list()
            self.redfish["Links"]["ComputerSystems"].append(system)

        if self.zone_ids:
            self.redfish["Links"]["Zones"] = list()
            location_id = self.server_hardware["locationUri"].split("/")[-1]

            for zone_id in self.zone_ids:
                _, encl_id = ZoneService\
                    .split_zone_id_to_spt_uuid_and_enclosure_id(zone_id)

                zone = dict()
                if (encl_id and encl_id == location_id) or not encl_id:
                    zone["@odata.id"] = \
                        "/redfish/v1/CompositionService/ResourceZones/" \
                        + zone_id

                    self.redfish["Links"]["Zones"].append(zone)
