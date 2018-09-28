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
from flask_api import status

from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api.resource_block_computer_system \
    import ResourceBlockComputerSystem
from oneview_redfish_toolkit.api.resource_block_ethernet_interface \
    import ResourceBlockEthernetInterface
from oneview_redfish_toolkit.api.server_hardware_resource_block \
    import ServerHardwareResourceBlock
from oneview_redfish_toolkit.api.server_profile_template_resource_block \
    import ServerProfileTemplateResourceBlock
from oneview_redfish_toolkit.api.storage_resource_block \
    import StorageResourceBlock
from oneview_redfish_toolkit.blueprints.util.response_builder \
    import ResponseBuilder
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit.services.manager_service import \
    get_manager_uuid
from oneview_redfish_toolkit.services.zone_service import ZoneService
from oneview_redfish_toolkit.single_oneview_context import single_oneview

resource_block = Blueprint("resource_block", __name__)


@resource_block.route(ResourceBlock.BASE_URI + "/<uuid>", methods=["GET"])
@single_oneview
def get_resource_block(uuid):
    """Get the Redfish ResourceBlock for a given UUID.

        Return ResourceBlock redfish JSON for a given UUID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock.
    """
    try:
        zone_service = ZoneService(g.oneview_client)
        resource = _get_oneview_resource(uuid)
        category = resource["category"]

        if category == "server-hardware":
            result_resource_block = _build_computer_system_resource_block(
                uuid, resource)

        elif category == "server-profile-templates":
            zone_ids = zone_service.get_zone_ids_by_templates([resource])
            if not zone_ids:
                raise OneViewRedfishError("Zone not found "
                                          "to ResourceBlock {}".format(uuid))

            result_resource_block = \
                ServerProfileTemplateResourceBlock(uuid, resource, zone_ids)

        elif category == "drives":
            drive_uuid = resource["uri"].split("/")[-1]
            drive_index_trees_uri = \
                "/rest/index/trees/rest/drives/{}?parentDepth=3"
            drive_index_trees = g.oneview_client.connection.get(
                drive_index_trees_uri.format(drive_uuid))

            server_profile_templs = \
                g.oneview_client.server_profile_templates.get_all()

            zone_ids = zone_service.get_zone_ids_by_templates(
                server_profile_templs)

            result_resource_block = StorageResourceBlock(
                resource, drive_index_trees, zone_ids)

        else:
            raise OneViewRedfishError('Resource block not found')

        return ResponseBuilder.success(
            result_resource_block,
            {"ETag": "W/" + resource["eTag"]})

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)


@resource_block.route(
    ResourceBlock.BASE_URI + "/<uuid>/Systems/1", methods=["GET"])
@single_oneview
def get_resource_block_computer_system(uuid):
    """Get Computer System of a Resource Block

        Return ResourceBlock Computer System redfish JSON for a given
        UUID. Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock Computer System.
    """

    server_hardware = g.oneview_client.server_hardware.get(uuid)
    manager_uuid = get_manager_uuid(uuid)

    computer_system = ResourceBlockComputerSystem(
        server_hardware, manager_uuid)

    return ResponseBuilder.success(
        computer_system,
        {"ETag": "W/" + server_hardware["eTag"]})


@resource_block.route(
    ResourceBlock.BASE_URI + "/<uuid>/EthernetInterfaces/<id>",
    methods=["GET"])
@single_oneview
def get_resource_block_ethernet_interface(uuid, id):
    """Get the Redfish ResourceBlock of type Network for the given UUID and ID.

        Return ResourceBlock redfish JSON for a given UUID and ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock.
    """

    try:
        server_profile_template = \
            g.oneview_client.server_profile_templates.get(uuid)

        conn_settings = server_profile_template["connectionSettings"]
        connection = None

        for conn in conn_settings["connections"]:
            if str(conn["id"]) == id:
                connection = conn
                break

        if not connection:
            raise OneViewRedfishError("Ethernet interface not found")

        network = \
            g.oneview_client.index_resources.get(connection["networkUri"])

        ethernet_interface = ResourceBlockEthernetInterface(
            server_profile_template, connection, network)

        return ResponseBuilder.success(
            ethernet_interface,
            {"ETag": "W/" + server_profile_template["eTag"]})

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)


def _get_oneview_resource(uuid):
    drives_param = "/rest/drives/" + uuid

    cached_categ = category_resource.get_category_by_resource_id(uuid) or \
        category_resource.get_category_by_resource_id(drives_param)

    if cached_categ:
        resource_uuid = uuid

        if cached_categ.resource == 'index_resources':
            resource_uuid = drives_param

        resource = getattr(g.oneview_client, cached_categ.resource)
        function = getattr(resource, cached_categ.function)

        return function(resource_uuid)

    categories = [
        {"func": g.oneview_client.server_hardware.get, "param": uuid},
        {"func": g.oneview_client.server_profile_templates.get, "param": uuid},
        {"func": g.oneview_client.index_resources.get, "param": drives_param}
    ]

    for category in categories:
        try:
            resource = category["func"](category["param"])

            return resource
        except HPOneViewException as e:
            if e.oneview_response["errorCode"] == 'RESOURCE_NOT_FOUND':
                pass
            else:
                raise  # Raise any unexpected errors

    raise OneViewRedfishError("Could not find resource block with id " + uuid)


def _build_computer_system_resource_block(uuid, server_hardware):
    eg_uri = server_hardware["serverGroupUri"]
    sht_uri = server_hardware["serverHardwareTypeUri"]

    filters = list()
    filters.append("enclosureGroupUri='{}'".format(eg_uri))
    filters.append("serverHardwareTypeUri='{}'".format(sht_uri))

    server_profile_templs = g.oneview_client \
        .server_profile_templates.get_all(filter=filters)

    zone_service = ZoneService(g.oneview_client)
    zone_ids = zone_service.get_zone_ids_by_templates(server_profile_templs)

    # Build ResourceBlock object and validates it
    return ServerHardwareResourceBlock(uuid, server_hardware, zone_ids)
