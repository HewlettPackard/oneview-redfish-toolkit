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
from flask import request
from flask_api import status

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api.vlan_network_interface \
    import VLanNetworkInterface
from oneview_redfish_toolkit.api.vlan_network_interface_collection \
    import VLanNetworkInterfaceCollection
from oneview_redfish_toolkit.blueprints.util.response_builder \
    import ResponseBuilder

vlan_network_interface = Blueprint("vlan_network_interface", __name__)


@vlan_network_interface.route(
    ResourceBlock.BASE_URI +
    "/<uuid>/EthernetInterfaces/<id>/VLANs", methods=["GET"])
@vlan_network_interface.route(
    ComputerSystem.BASE_URI +
    "/<uuid>/EthernetInterfaces/<id>/VLANs", methods=["GET"])
def get_vlan_network_interface_collection(uuid, id):
    """Get Redfish VLanNetworkInterfaceCollection for the given UUID and ID.

        Return VLanNetworkInterfaceCollection redfish JSON for a given
        ServerProfileTemplate UUID and connection ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with VLanNetworkInterfaceCollection.
    """

    try:
        server_profile_template = \
            g.oneview_client.server_profile_templates.get(uuid)

        connSettings = server_profile_template["connectionSettings"]
        connection = None

        for conn in connSettings["connections"]:
            if str(conn["id"]) == id:
                connection = conn
                break

        if not connection:
            raise OneViewRedfishError("Ethernet interface not found")

        network_set = \
            g.oneview_client.network_sets.get(connection["networkUri"])

        vlan_collection = \
            VLanNetworkInterfaceCollection(network_set, request.path)

        return ResponseBuilder.success(vlan_collection)

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)


@vlan_network_interface.route(
    ResourceBlock.BASE_URI +
    "/<uuid>/EthernetInterfaces/<id>/VLANs/<vlan_id>", methods=["GET"])
@vlan_network_interface.route(
    ComputerSystem.BASE_URI +
    "/<uuid>/EthernetInterfaces/<id>/VLANs/<vlan_id>", methods=["GET"])
def get_vlan_network_interface(uuid, id, vlan_id):
    """Get the Redfish VLanNetworkInterface for the given UUID, ID and VLanID.

        Return VLanNetowrkInterface redfish JSON for a given
        ServerProfileTemplate UUID, EthernetInterface ID and a VLan ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock.
    """

    ethernet_network = \
        g.oneview_client.ethernet_networks.get(vlan_id)

    vlan = VLanNetworkInterface(ethernet_network, request.path)

    return ResponseBuilder.success(vlan)
