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

from oneview_redfish_toolkit.api.zone_collection import ZoneCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit.services.zone_service import ZoneService

zone_collection = Blueprint("zone_collection", __name__)


@zone_collection.route(ZoneCollection.BASE_URI + "/", methods=["GET"])
def get_zone_collection():
    """Get the Redfish Zone Collection.

        Return ZoneCollection redfish JSON.

        Logs exception of any error and return Internal
        Server Error or Not Found.

        Returns:
            JSON: Redfish json with ZoneCollection.
    """

    server_profile_templates = \
        g.oneview_client.server_profile_templates.get_all()

    zone_service = ZoneService(g.oneview_client)
    zone_ids = zone_service.get_zone_ids_by_templates(server_profile_templates)

    zc = ZoneCollection(zone_ids)

    return ResponseBuilder.success(zc)


def _get_enclosures_uris_by_template(server_profile_template):
    log_encl_assoc_uri = "/rest/index/associations/resources" \
        "?parenturi={}&category=logical-enclosures"\
        .format(server_profile_template["enclosureGroupUri"])
    logical_encl_assoc = g.oneview_client.connection.get(log_encl_assoc_uri)
    members = logical_encl_assoc["members"]
    enclosure_uris = []
    for member in members:
        log_encl_uri = member["childResource"]["uri"]
        logical_encl = g.oneview_client.logical_enclosures.get(log_encl_uri)
        enclosure_uris += logical_encl["enclosureUris"]

    #  the set keeps the elements without repetition
    enclosure_uris = list(set(enclosure_uris))
    enclosure_uris.sort()

    return enclosure_uris
