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

# Python libs
import logging

# 3rd party libs
from flask import abort
from flask import Blueprint
from flask import g
from flask import request
from flask import Response
from flask_api import status

# Own libs
from oneview_redfish_toolkit.api.blade_chassis import BladeChassis
from oneview_redfish_toolkit.api.enclosure_chassis import EnclosureChassis
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.rack_chassis import RackChassis
from oneview_redfish_toolkit.api.util.power_option import OneViewPowerOption
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit.services.manager_service import \
    get_manager_uuid

chassis = Blueprint("chassis", __name__)


@chassis.route("/redfish/v1/Chassis/<uuid>", methods=["GET"])
def get_chassis(uuid):
    """Get the Redfish Chassis.

        Get method to return Chassis JSON when
        /redfish/v1/Chassis/id is requested.

        Returns:
            JSON: JSON with Chassis.
    """
    category = ''
    cached_category = category_resource.get_category_by_resource_id(uuid)

    if cached_category:
        category = cached_category.resource.replace('_', '-')
    else:
        resource_index = g.oneview_client.index_resources.get_all(
            filter='uuid=' + uuid
        )
        if not resource_index:
            abort(status.HTTP_404_NOT_FOUND,
                  "Chassis {} not found".format(uuid))

        category = resource_index[0]["category"]

    manager_uuid = get_manager_uuid(uuid)

    if category == 'server-hardware':
        server_hardware = g.oneview_client.server_hardware.get(uuid)
        etag = server_hardware['eTag']
        ch = BladeChassis(server_hardware, manager_uuid)
    elif category == 'enclosures':
        enclosure = g.oneview_client.enclosures.get(uuid)
        etag = enclosure['eTag']
        enclosure_environment_config = g.oneview_client.enclosures. \
            get_environmental_configuration(uuid)
        ch = EnclosureChassis(
            enclosure,
            enclosure_environment_config,
            manager_uuid
        )
    elif category == 'racks':
        racks = g.oneview_client.racks.get(uuid)
        etag = racks['eTag']
        ch = RackChassis(racks)

    return ResponseBuilder.success(ch, {"ETag": "W/" + etag})


@chassis.route("/redfish/v1/Chassis/<uuid>/"
               "Actions/Chassis.Reset", methods=["POST"])
def change_server_hardware_power_state(uuid):
    """Change the Oneview power state for a specific Server hardware.

        Return ResetType Chassis redfish JSON for a
        given chassis UUID.
        Logs exception of any error and return abort.

        Returns:
            JSON: Redfish JSON with Chassis ResetType.

        Exceptions:
            q: When some OneView resource was not found.
            return abort(404)

            OneViewRedfishError: When occurs a power state mapping error.
            return abort(400)

            Exception: Unexpected error.
            return abort(500)
    """
    try:
        try:
            reset_type = request.get_json()["ResetType"]
        except KeyError:
            invalid_key = list(request.get_json())[0]  # gets invalid key name
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key: {}".format(invalid_key)})

        resource_index = g.oneview_client.index_resources.get_all(
            filter='uuid=' + uuid
        )
        if not resource_index:
            abort(status.HTTP_404_NOT_FOUND,
                  "Chassis {} not found".format(uuid))

        category = resource_index[0]["category"]
        if category == 'server-hardware':
            # Gets ServerHardware for given UUID
            sh = g.oneview_client.server_hardware.get(uuid)

            # Gets power configuration based on OneView pattern
            oneview_power_configuration = \
                OneViewPowerOption.get_oneview_power_configuration(
                    sh, reset_type
                )

            # Changes the ServerHardware power state
            g.oneview_client.server_hardware.update_power_state(
                oneview_power_configuration, uuid)

            return Response(
                response='{"ResetType": "%s"}' % reset_type,
                status=status.HTTP_200_OK,
                mimetype='application/json')

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Mapping error: {}'.format(e))

        if e.msg["errorCode"] == "NOT_IMPLEMENTED":
            abort(status.HTTP_501_NOT_IMPLEMENTED, e.msg['message'])
        else:
            abort(status.HTTP_400_BAD_REQUEST, e.msg['message'])
