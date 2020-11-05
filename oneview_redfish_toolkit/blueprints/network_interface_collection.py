# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.network_interface_collection \
    import NetworkInterfaceCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

network_interface_collection = Blueprint(
    "network_interface_collection", __name__)


@network_interface_collection.route(
    ComputerSystem.BASE_URI + "/<server_profile_uuid>/NetworkInterfaces/",
    methods=["GET"])
def get_network_interface_collection(server_profile_uuid):
    """Get the Redfish Network Interfaces Collection.

    Return NetworkInterfaceCollection Redfish JSON.
    """
    profile = g.oneview_client.server_profiles.get_by_id(
        server_profile_uuid).data
    server_hardware = g.oneview_client.server_hardware\
        .get_by_uri(profile["serverHardwareUri"]).data

    nic = NetworkInterfaceCollection(profile, server_hardware)

    return ResponseBuilder.success(nic)
