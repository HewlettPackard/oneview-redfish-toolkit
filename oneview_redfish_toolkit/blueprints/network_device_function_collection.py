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
from flask import Response
from flask_api import status

from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.network_device_function_collection import\
    NetworkDeviceFunctionCollection

from oneview_redfish_toolkit import util

import logging

network_device_function_collection = Blueprint(
    "network_device_function_collection", __name__)


@network_device_function_collection.route(
    "/redfish/v1/Chassis/<uuid>/NetworkAdapters/<device_id>"
    "/NetworkDeviceFunctions/", methods=["GET"])
def get_network_device_function_collection(uuid, device_id):
    """Get the Redfish Network Interfaces Collection.

    Return NetworkDeviceFunctionCollection Redfish JSON.
    """
    try:
        oneview_client = util.get_oneview_client()

        server_hardware = oneview_client.server_hardware.get(uuid)

        ndfc = NetworkDeviceFunctionCollection(device_id, server_hardware)

        json_str = ndfc.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")

    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            logging.warning('Server hardware UUID {} not found'.format(uuid))
            abort(status.HTTP_404_NOT_FOUND, "Server hardware not found")
        elif e.msg.find("server-hardware") >= 0:
            logging.error(
                'OneView Exception while looking for '
                'server hardware: {}'.format(e)
            )
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logging.error('Unexpected OneView Exception: {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # In case of error print exception and abort
        logging.error('Unexpected error: '.format(e))
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
