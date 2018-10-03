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
import logging

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api import status_mapping
from oneview_redfish_toolkit.api.zone_collection import ZoneCollection
from oneview_redfish_toolkit.services.zone_service import ZoneService


class StorageResourceBlock(ResourceBlock):
    """Creates a ResourceBlock Redfish dict for Storage Drive

        Populates self.redfish with Drive data retrieved from OneView.
    """

    def __init__(self, drive, drive_index_trees, zone_ids):
        """StorageResourceBlock constructor

            Populates self.redfish with the contents of drive

            Args:
                drive: OneView Drive dict
                drive_index_trees: Drives index trees dict
                zone_ids: List of Zone Ids that this Resource Block belongs to
        """
        uuid = drive["uri"].split("/")[-1]
        super().__init__(uuid, drive)
        self.redfish["ResourceBlockType"] = ["Storage"]
        self.redfish["Status"] = status_mapping.STATUS_MAP.get(drive["status"])

        if drive["attributes"]["available"] == "yes":
            composit_state = "Unused"
        else:
            composit_state = "Composed"

        self.redfish["CompositionStatus"]["CompositionState"] = composit_state
        self.redfish["CompositionStatus"]["SharingCapable"] = False
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["Links"]["ComputerSystems"] = list()
        self.redfish["Links"]["Zones"] = list()
        self._fill_link_members(drive_index_trees, zone_ids)

        self.redfish["Storage"] = [
            {
                "@odata.id": self.redfish["@odata.id"] + "/Storage/1"
            }
        ]

        self._validate()

    def _fill_link_members(self, drive_index_trees, zone_ids):
        sp_uuid = self._get_server_profile_uuid(drive_index_trees)
        if sp_uuid:
            system_dict = {
                "@odata.id": ComputerSystem.BASE_URI + "/" + sp_uuid
            }
            self.redfish["Links"]["ComputerSystems"].append(system_dict)

        current_encl_id = self._get_enclosure_uuid(drive_index_trees)
        if current_encl_id:
            for zone_id in zone_ids:
                _, encl_id = ZoneService\
                    .split_zone_id_to_spt_uuid_and_enclosure_id(zone_id)

                if encl_id == current_encl_id:
                    zone_dict = {
                        "@odata.id": ZoneCollection.BASE_URI + "/" + zone_id
                    }
                    self.redfish["Links"]["Zones"].append(zone_dict)

    def _get_server_profile_uuid(self, drive_index_trees):
        try:
            bay = drive_index_trees["parents"]["DRIVE_BAY_TO_DRIVE_ASSOC"][0]
            sas_jbod = \
                bay["parents"]["SAS_LOGICAL_JBOD_TO_DRIVEBAYS_ASSOCIATION"][0]
            server_profile = \
                sas_jbod["parents"]["SERVERPROFILE_TO_SLJBOD_ASSOCIATION"][0]
            server_profile_uuid = \
                server_profile["resource"]["uri"].split("/")[-1]
        except KeyError as e:
            logging.debug("The key {} was not found inside "
                          "'drive index trees dict' from the Oneview when "
                          "trying get the server profile uuid"
                          .format(e.args[0]))
            server_profile_uuid = None

        return server_profile_uuid

    def _get_enclosure_uuid(self, drive_index_trees):
        try:
            bay = drive_index_trees["parents"]["DRIVE_BAY_TO_DRIVE_ASSOC"][0]
            drive_encl = \
                bay["parents"]["DRIVE_ENCLOSURE_TO_DRIVE_BAY_ASSOC"][0]
            enclosure = \
                drive_encl["parents"]["ENCLOSURE_TO_BLADE"][0]
            enclosure_id = \
                enclosure["resource"]["attributes"]["uuid"]
        except KeyError as e:
            logging.debug("The key {} was not found inside "
                          "'drive index trees dict' from the Oneview when "
                          "trying get the enclosure uuid"
                          .format(e.args[0]))
            enclosure_id = None

        return enclosure_id
