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
from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api.vlan_network_interface \
    import VLanNetworkInterface
from oneview_redfish_toolkit.api.vlan_network_interface_collection \
    import VLanNetworkInterfaceCollection
from oneview_redfish_toolkit.blueprints.util.response_builder \
    import ResponseBuilder

vlan_network_interface = Blueprint("vlan_network_interface", __name__)


@vlan_network_interface.route(
    ComputerSystem.BASE_URI +
    "/<sp_uuid>/EthernetInterfaces/<connection_id>/VLANs", methods=["GET"])
def get_vlan_network_interface_collection_sp(sp_uuid, connection_id):
    """Get Redfish VLanNetworkInterfaceCollection for the given UUID and ID.

        Return VLanNetworkInterfaceCollection redfish JSON for a given
        ServerProfile UUID and connection ID.

        Returns:
            JSON: Redfish json with VLanNetworkInterfaceCollection.
    """

    server_profile = \
        g.oneview_client.server_profiles.get(sp_uuid)

    connection = \
        _get_connection_oneview_resource(server_profile,
                                         connection_id)

    vlan_collection = \
        _get_vlan_network_interface_collection(connection["networkUri"])

    return ResponseBuilder.success(vlan_collection)


@vlan_network_interface.route(
    ResourceBlock.BASE_URI +
    "/<spt_uuid>/EthernetInterfaces/<connection_id>/VLANs", methods=["GET"])
def get_vlan_network_interface_collection_spt(spt_uuid, connection_id):
    """Get Redfish VLanNetworkInterfaceCollection for the given UUID and ID.

        Return VLanNetworkInterfaceCollection redfish JSON for a given
        ServerProfileTemplate UUID and connection ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with VLanNetworkInterfaceCollection.
    """

    server_profile_template = \
        g.oneview_client.server_profile_templates.get(spt_uuid)

    connection = \
        _get_connection_oneview_resource(server_profile_template,
                                         connection_id)

    vlan_collection = \
        _get_vlan_network_interface_collection(connection["networkUri"])

    return ResponseBuilder.success(vlan_collection)


def _get_connection_oneview_resource(oneview_resource, connection_id):
    """Get OneView Connection for the given resource and ID.

        Return OneView Connection a given OneView resource and connection ID.
        Logs exception of any error and Not Found.
        Returns:
            JSON: OneView Connection
    """

    conn_settings = oneview_resource["connectionSettings"]
    connection = None

    for conn in conn_settings["connections"]:
        if str(conn["id"]) == connection_id:
            connection = conn
            break

    if not connection:
        msg = "Ethernet interface not found"
        logging.exception('Unexpected error: {}'.format(msg))
        abort(status.HTTP_404_NOT_FOUND, msg)

    return connection


def _get_vlan_network_interface_collection(network_uri):
    """Get Redfish VLanNetworkInterfaceCollection for the given Network URI.

        Return VLanNetworkInterfaceCollection redfish JSON for a given
        Network Set URI.

        Returns:
            JSON: Redfish json with VLanNetworkInterfaceCollection.
    """

    network_set = g.oneview_client.network_sets.get(network_uri)

    vlan_collection = \
        VLanNetworkInterfaceCollection(network_set, request.path)

    return vlan_collection


@vlan_network_interface.route(
    ComputerSystem.BASE_URI +
    "/<sp_uuid>/EthernetInterfaces/<conn_id>/VLANs/<vlan_id>",
    methods=["GET"])
def get_vlan_network_interface_sp(sp_uuid, conn_id, vlan_id):
    """Get the Redfish VLanNetworkInterface for the given UUID, ID and VLanID.

        Return VLanNetowrkInterface redfish JSON for a given
        ServerProfileTemplate UUID, EthernetInterface ID and a VLan ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock.
    """

    server_profile = \
        g.oneview_client.server_profiles.get(sp_uuid)

    _get_connection_oneview_resource(server_profile, conn_id)

    ethernet_network = \
        g.oneview_client.ethernet_networks.get(vlan_id)

    vlan = VLanNetworkInterface(ethernet_network, request.path)

    return ResponseBuilder.success(vlan)


@vlan_network_interface.route(
    ResourceBlock.BASE_URI +
    "/<spt_uuid>/EthernetInterfaces/<conn_id>/VLANs/<vlan_id>",
    methods=["GET"])
def get_vlan_network_interface_spt(spt_uuid, conn_id, vlan_id):
    """Get the Redfish VLanNetworkInterface for the given UUID, ID and VLanID.

        Return VLanNetowrkInterface redfish JSON for a given
        ServerProfileTemplate UUID, EthernetInterface ID and a VLan ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock.
    """

    server_profile_template = \
        g.oneview_client.server_profile_templates.get(spt_uuid)

    _get_connection_oneview_resource(server_profile_template, conn_id)

    ethernet_network = \
        g.oneview_client.ethernet_networks.get(vlan_id)

    vlan = VLanNetworkInterface(ethernet_network, request.path)

    return ResponseBuilder.success(vlan)
