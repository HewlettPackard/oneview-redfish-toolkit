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

# Python libs
import logging

# 3rd party libs
from flask import abort
from flask import Blueprint
from flask import Response
from flask_api import status

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.network_interface import NetworkInterface
from oneview_redfish_toolkit import util


network_interface = Blueprint("network_interface", __name__)


@network_interface.route(
    "/redfish/v1/Systems/<uuid>/NetworkInterfaces/<device_id>",
    methods=["GET"])
def get_network_interface(uuid, device_id):
    """Get the Redfish NetworkInterface for a given UUID and device_id.

        Return NetworkInterface Redfish JSON for a given hardware UUID
        and device_id.

        Parameters:
            uuid: the UUID of the server_hardware
            device_id: The id of the network device

        Returns:
            JSON: Redfish json with Thermal

        Exceptions:
            When hardware is not found calls abort(404)
            When other errors occur calls abort(500)

    """
    try:
        oneview_client = util.get_oneview_client()

        server_hardware = oneview_client.server_hardware.get(uuid)

        ni = NetworkInterface(device_id, server_hardware)

        json_str = ni.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.error(e)
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            abort(status.HTTP_404_NOT_FOUND, "Server hardware not found")
        else:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
