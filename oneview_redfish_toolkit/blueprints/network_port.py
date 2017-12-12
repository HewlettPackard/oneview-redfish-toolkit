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
from flask import g
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# own libs

from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishError
from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api.network_port import \
    NetworkPort

network_port = Blueprint("network_port", __name__)


@network_port.route(
    "/redfish/v1/Chassis/<uuid>/NetworkAdapters/<device_id>"
    "/NetworkPorts/<port_id>",
    methods=["GET"])
def get_network_port(uuid, device_id, port_id):
    """Get the Redfish NetworkPort for a given UUID, device_id and port_id.

        Return NetworkPort Redfish JSON for a given hardware UUID, device_id
        and port_id.

        Parameters:
            uuid: the UUID of the server_hardware
            device_id: The id of the network device
            port_id: The id of the port

        Returns:
            JSON: Redfish json with NetworkPort

        Exceptions:
            When hardware is not found calls abort(404)
            When other errors occur calls abort(500)

    """
    try:
        # Initial validation of device_id
        device_id_validation = int(device_id)

        server_hardware = g.oneview_client.server_hardware.get(uuid)

        # Final validation of device_id
        if device_id_validation - 1 < 0 or (device_id_validation - 1) >= \
            len(server_hardware["portMap"]["deviceSlots"]):
            raise OneViewRedfishResourceNotFoundError(
                device_id, "Network adapter")

        np = NetworkPort(device_id, port_id, server_hardware)

        json_str = np.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except ValueError:
        # Failed to convert device_id to int
        logging.exception(
            "Failed to convert device id {} to integer.".format(device_id))
        abort(status.HTTP_404_NOT_FOUND, "Network adapter not found")
    except OneViewRedfishResourceNotFoundError as e:
        logging.exception(e.msg)
        abort(status.HTTP_404_NOT_FOUND, e.msg)
    except OneViewRedfishError as e:
        logging.exception(e.msg)
        abort(status.HTTP_404_NOT_FOUND, e.msg)
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            abort(status.HTTP_404_NOT_FOUND, "Server hardware not found")
        else:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
