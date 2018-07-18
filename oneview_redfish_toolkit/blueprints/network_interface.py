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
from flask_api import status

# own libs
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api.network_interface import NetworkInterface
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

network_interface = Blueprint("network_interface", __name__)


@network_interface.route(
    ComputerSystem.BASE_URI +
    "/<server_profile_uuid>/NetworkInterfaces/<device_id>",
    methods=["GET"])
def get_network_interface(server_profile_uuid, device_id):
    """Get the Redfish NetworkInterface for a given UUID and device_id.

        Return NetworkInterface Redfish JSON for a given hardware UUID
        and device_id.

        Parameters:
            server_profile_uuid: the UUID of the server profile
            device_id: The id of the network device

        Returns:
            JSON: Redfish json with NetworkInterface

        Exceptions:
            When server profile or hardware is not found calls abort(404)
            When other errors occur calls abort(500)

    """
    try:
        device_id_validation = int(device_id)

        profile = g.oneview_client.server_profiles.get(server_profile_uuid)
        server_hardware = g.oneview_client.server_hardware\
            .get(profile["serverHardwareUri"])

        if (device_id_validation - 1) < 0 or (device_id_validation - 1) >= \
                len(server_hardware["portMap"]["deviceSlots"]):
            raise OneViewRedfishResourceNotFoundError(
                device_id, "Network interface")

        ni = NetworkInterface(device_id, profile, server_hardware)

        return ResponseBuilder.success(ni)

    except ValueError:
        # Failed to convert device_id to int
        logging.exception(
            "Failed to convert device id {} to integer.".format(device_id))
        abort(status.HTTP_404_NOT_FOUND, "Network interface not found")
    except OneViewRedfishResourceNotFoundError as e:
        logging.exception(e.msg)
        abort(status.HTTP_404_NOT_FOUND, e.msg)
