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


zone = Blueprint("zone", __name__)


@zone.route(ZoneCollection.BASE_URI + "/<uuid>", methods=["GET"])
def get_zone(uuid):
    """Get the Redfish Zone.

        Return Resource Zone redfish JSON.

        Logs exception of any error and return Internal
        Server Error or Not Found.

        Returns:
            JSON: Redfish json with Resource Zone.
    """
    profile_template = g.oneview_client.server_profile_templates.get(uuid)

    enclosure_group_resource = \
        _get_enclosure_group_index_trees(profile_template)

    drives = g.oneview_client.index_resources \
        .get_all(category="drives", count=10000)

    zone_data = Zone(profile_template, enclosure_group_resource, drives)

    return ResponseBuilder.success(zone_data)


def _get_enclosure_group_index_trees(profile_template):
    encl_group_uri = profile_template['enclosureGroupUri']
    encl_group_index_trees_uri = "/rest/index/trees{}?childDepth=2"
    encl_group_index_trees = g.oneview_client.connection.get(
        encl_group_index_trees_uri.format(encl_group_uri))

    return encl_group_index_trees
