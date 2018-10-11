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
from oneview_redfish_toolkit.config import \
    COUNTER_LOGGER_NAME
from oneview_redfish_toolkit.services import logging_service
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

    spt_count = len(server_profile_templates)
    zone_count = len(zc.redfish["Members"])
    logging_service.debug(
        COUNTER_LOGGER_NAME,
        "ServerProfileTemplates retrieved: " + str(spt_count),
        "Zones listed: " + str(zone_count))

    return ResponseBuilder.success(zc)
