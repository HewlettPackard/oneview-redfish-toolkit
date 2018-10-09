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

from flask import Blueprint
from flask import g

from oneview_redfish_toolkit.api.zone import Zone
from oneview_redfish_toolkit.api.zone_collection import ZoneCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit.config import \
    COUNTER_LOGGER_NAME
from oneview_redfish_toolkit.services import logging_service
from oneview_redfish_toolkit.services.zone_service import ZoneService

zone = Blueprint("zone", __name__)


@zone.route(ZoneCollection.BASE_URI + "/<zone_uuid>", methods=["GET"])
def get_zone(zone_uuid):
    """Get the Redfish Zone.

        Return Resource Zone redfish JSON.

        Logs exception of any error and return Internal
        Server Error or Not Found.

        Returns:
            JSON: Redfish json with Resource Zone.
    """
    template_id, enclosure_id = ZoneService.\
        split_zone_id_to_spt_uuid_and_enclosure_id(zone_uuid)

    profile_template = g.oneview_client.server_profile_templates.get(
        template_id)
    sh_type_uri = profile_template['serverHardwareTypeUri']
    enclosure_name = None

    if enclosure_id:
        enclosure = g.oneview_client.enclosures.get(enclosure_id)
        enclosure_name = enclosure["name"]
        drives = _get_drives(enclosure)
        sh_filter = [
            "locationUri='{}'".format(enclosure['uri']),
            "serverHardwareTypeUri='{}'".format(sh_type_uri)
        ]
    else:
        drives = []
        enclosure_group_uri = profile_template["enclosureGroupUri"]
        sh_filter = [
            "serverGroupUri='{}'".format(enclosure_group_uri),
            "serverHardwareTypeUri='{}'".format(sh_type_uri)
        ]

    server_hardware_list = g.oneview_client.server_hardware.get_all(
        filter=sh_filter)

    zone_data = Zone(zone_uuid, profile_template, server_hardware_list,
                     enclosure_name, drives)

    sh_count = len(server_hardware_list)
    blocks_count = len(zone_data.redfish["Links"]["ResourceBlocks"])
    logging_service.debug(
        COUNTER_LOGGER_NAME,
        "Drives retrieved: " + str(len(drives)),
        "ServerHardware retrieved: " + str(sh_count),
        "ResourceBlocks listed on Zone: " + str(blocks_count))

    return ResponseBuilder.success(zone_data)


def _get_drives(enclosure):
    drive_encl_assoc_uri = "/rest/index/associations/resources" \
                           "?parenturi={}&category=drive-enclosures"\
        .format(enclosure["uri"])
    drive_encl_assoc = g.oneview_client.connection.get(drive_encl_assoc_uri)
    get_drives_uri = '/rest/index/resources' \
        '?category=drives&count=10000' \
        '&filter="driveEnclosureUri:{}"'
    drives = []
    for member in drive_encl_assoc["members"]:
        drive_encl_uri = member["childResource"]["uri"]
        drives_index_list = g.oneview_client.connection.get(
            get_drives_uri.format(drive_encl_uri))
        drives += drives_index_list["members"]

    return drives
