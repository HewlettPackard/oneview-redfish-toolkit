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
from flask import request
from flask import Response
from flask_api import status

from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.network_interface_collection \
    import NetworkInterfaceCollection

from oneview_redfish_toolkit import util

import logging

network_interface_collection = Blueprint(
    "network_interface_collection", __name__)


@network_interface_collection.route(
    "/redfish/v1/Systems/<uuid>/NetworkInterfaces/", methods=["GET"])
def get_network_interface_collection(uuid):
    """Get the Redfish Network Interfaces Collection.

    Return NetworkInterfaceCollection Redfish JSON.
    """
    try:
        if util.config["redfish"]["authentication_mode"] == "session":
            # Recover session id
            session_id = request.headers.get('x-auth-token')
            # Recover OV connection
            oneview_client = util.get_oneview_client(session_id)
        else:
            oneview_client = util.get_oneview_client()

        server_hardware = oneview_client.server_hardware.get(uuid)

        nic = NetworkInterfaceCollection(server_hardware)

        json_str = nic.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")

    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            logging.warning('Server hardware UUID {} not found'.format(uuid))
            abort(status.HTTP_404_NOT_FOUND, "Server hardware not found")
        elif e.msg.find("server-hardware") >= 0:
            logging.exception(
                'OneView Exception while looking for '
                'server hardware: {}'.format(e)
            )
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logging.exception('Unexpected OneView Exception: {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # In case of error print exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
