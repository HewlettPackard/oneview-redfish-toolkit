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
from flask_api import status
from werkzeug.exceptions import abort

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.ethernet_interface import EthernetInterface
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

ethernet_interface = Blueprint("ethernet_interface", __name__)


@ethernet_interface.route(
    ComputerSystem.BASE_URI +
    "/<server_profile_uuid>/EthernetInterfaces/<eth_id>",
    methods=["GET"])
def get_ethernet_interface(server_profile_uuid, eth_id):
    """Get the Redfish Ethernet Interface.

    Return EthernetInterface Redfish JSON.
    """
    profile = g.oneview_client.server_profiles.get(server_profile_uuid)

    connections = profile["connectionSettings"]["connections"]

    connection = None
    for conn in connections:
        if str(conn["id"]) == str(eth_id):
            connection = conn
            break

    if connection is None:
        abort(status.HTTP_404_NOT_FOUND, "EthernetInterface {} not found"
              .format(eth_id))

    network_attrs = g.oneview_client.index_resources\
        .get(connection["networkUri"])

    ethernet = EthernetInterface(profile, connection, network_attrs)

    return ResponseBuilder.success(ethernet)
