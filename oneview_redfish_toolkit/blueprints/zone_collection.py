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

import logging

from flask import abort
from flask import Blueprint
from flask import g
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.zone_collection import ZoneCollection


zone_collection = Blueprint("zone_collection", __name__)


@zone_collection.route(
    "/redfish/v1/CompositionService/ResourceZones/", methods=["GET"])
def get_zone_collection():
    """Get the Redfish Zone Collection.

        Return ZoneCollection redfish JSON.

        Logs exception of any error and return Internal
        Server Error or Not Found.

        Returns:
            JSON: Redfish json with ZoneCollection.
    """

    try:
        # Gets all server profile templates
        server_profile_templates = \
            g.oneview_client.server_profile_templates.get_all()

        # Build ZoneCollection object and validates it
        zc = ZoneCollection(server_profile_templates)

        # Build redfish json
        json_str = zc.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except Exception as e:
        # In case of error print exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
