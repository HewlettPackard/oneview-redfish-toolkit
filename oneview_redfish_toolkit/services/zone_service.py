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
from oneview_redfish_toolkit.config import \
    COUNTER_LOGGER_NAME
from oneview_redfish_toolkit.services.computer_system_service import \
    ComputerSystemService
from oneview_redfish_toolkit.services import logging_service


class ZoneService(object):
    """Represents a Service class of Zone"""

    def __init__(self, oneview_client):
        """ZoneService constructor

            Args:
                oneview_client: client of Oneview SDK
        """
        self.ov_client = oneview_client

    @staticmethod
    def build_zone_id(spt_uuid_or_uri, enclosure_id_or_uri):
        """Builds a Zone ID based on IDs of server profile template and enclosure

            Args:
                spt_uuid_or_uri: UUID or URI of Server Profile Template
                enclosure_id_or_uri: ID or URI of Enclosure
        """
        spt_id = spt_uuid_or_uri.split("/")[-1]
        encl_id = enclosure_id_or_uri.split("/")[-1]
        return spt_id + "-" + encl_id

    @staticmethod
    def split_zone_id_to_spt_uuid_and_enclosure_id(zone_id):
        """Separates the Zone ID in two IDs:

            - Server Profile Template ID
            - Enclosure ID

            If Enclosure ID has not inside the Zone ID, the Enclosure ID
            returned will be None

            Result is a Tuple (spt_id, enclosure_id)

            Args:
                zone_id: the Zone ID
        """
        # verify if has enclosure id inside the zone_uuid,
        # the uuid has by default only 5 groups separated by hyphen
        uuid_groups = zone_id.split("-")

        if len(uuid_groups) > 5:
            enclosure_id = uuid_groups[-1]
            template_id = str.join("-", uuid_groups[:5])
        else:
            template_id = zone_id
            enclosure_id = None

        return template_id, enclosure_id

    def _get_enclosures_uris_by_template(self, server_profile_template,
                                         logical_encl_list):
        enclosure_uris = []
        for logical_encl in logical_encl_list:
            if logical_encl['enclosureGroupUri'] == \
                server_profile_template['enclosureGroupUri']:
                enclosure_uris += logical_encl['enclosureUris']

        #  the set keeps the elements without repetition
        enclosure_uris = list(set(enclosure_uris))
        enclosure_uris.sort()

        return enclosure_uris

    def get_zone_ids_by_templates(self, server_profile_templates):
        """Returns the Zone IDs by each Server Profile Template inside the list:

            If the list is empty, the result will be empty

            Args:
                server_profile_templates: the list of Server Profile Template
        """
        zone_ids = []
        enclosure_uris_with_valid_drive_enclosures = \
            self._get_enclosures_uris_with_valid_drive_enclosures()
        logical_encl_list = self.ov_client.logical_enclosures.get_all()
        for template in server_profile_templates:
            template_id = template["uri"].split("/")[-1]
            controller = ComputerSystemService.get_storage_controller(template)
            if controller:
                enclosures_uris_by_spt = self._get_enclosures_uris_by_template(
                    template, logical_encl_list)
                enclosures_uris = set(enclosures_uris_by_spt)\
                    .intersection(enclosure_uris_with_valid_drive_enclosures)

                for encl_uri in sorted(enclosures_uris):
                    zone_id = ZoneService.build_zone_id(template_id, encl_uri)
                    zone_ids.append(zone_id)
            else:
                zone_ids.append(template_id)

        return zone_ids

    def _get_enclosures_uris_with_valid_drive_enclosures(self):
        valid_enclosures_uris = list()
        drive_enclosures_list = self.ov_client.drive_enclosures.get_all()

        for drive_encl in drive_enclosures_list:
            # Check if have valid driver enclosure
            if drive_encl["driveBays"]:
                # Get enclosure uri from driver enclosure
                for location_entry in \
                    drive_encl['driveEnclosureLocation']['locationEntries']:
                    if location_entry['type'] == 'Enclosure':
                        valid_enclosures_uris.append(location_entry['value'])
                        break

        drive_encl_count = len(drive_enclosures_list)
        valid_encl_count = len(valid_enclosures_uris)
        logging_service.debug(COUNTER_LOGGER_NAME,
                              "Drive Enclosures retrieved: " +
                              str(drive_encl_count),
                              "Valid Enclosures: " + str(valid_encl_count))

        return valid_enclosures_uris
