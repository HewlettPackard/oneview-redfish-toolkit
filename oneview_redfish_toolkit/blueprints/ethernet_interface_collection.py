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

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.ethernet_interface_collection import \
    EthernetInterfaceCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

ethernet_interface_collection = Blueprint(
    "ethernet_interface_collection", __name__)


@ethernet_interface_collection.route(
    ComputerSystem.BASE_URI + "/<server_profile_uuid>/EthernetInterfaces/",
    methods=["GET"])
def get_ethernet_interface_collection(server_profile_uuid):
    """Get the Redfish Ethernet Interfaces Collection.

    Return EthernetInterfaceCollection Redfish JSON.
    """
    profile = g.oneview_client.server_profiles.get(server_profile_uuid)

    ethernet_collection = EthernetInterfaceCollection(profile)

    return ResponseBuilder.success(ethernet_collection)
