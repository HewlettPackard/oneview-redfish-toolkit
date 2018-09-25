# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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

from flask import abort
from flask import Blueprint
from flask import g
from flask_api import status

from oneview_redfish_toolkit.api.network_port_collection \
    import NetworkPortCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder


network_port_collection = Blueprint("network_port_collection", __name__)


@network_port_collection.route(
    "/redfish/v1/Chassis/<server_hardware_uuid>/NetworkAdapters/"
    "<int:device_id>/NetworkPorts/", methods=["GET"])
def get_network_port_collection(server_hardware_uuid, device_id):
    """Get the Redfish Network Port Collection.

        Return NetworkPortCollection Redfish JSON.
    """

    if device_id < 1:
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    server_hardware = g.oneview_client. \
        server_hardware.get(server_hardware_uuid)

    npc = NetworkPortCollection(server_hardware, device_id)

    return ResponseBuilder.success(npc)
