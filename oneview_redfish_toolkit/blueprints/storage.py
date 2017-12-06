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
from flask import request
from flask import Response
from flask_api import status

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.storage import Storage
from oneview_redfish_toolkit import util

storage = Blueprint("storage", __name__)


@storage.route("/redfish/v1/Systems/<uuid>/Storage/1", methods=["GET"])
def get_storage(uuid):
    """Get the Redfish Storage for a given UUID.

        Return Storage Redfish JSON for a given hardware UUID.
        Logs exception of any error and return abort(500)
        Internal Server Error.

        Returns:
            JSON: Redfish json with Storage
            When hardware or hardware type is not found calls abort(404)

        Exceptions:
            Logs the exception and call abort(500)

    """
    try:
        if util.config["redfish"]["authentication_mode"] == "session":
            # Revocer session id
            session_id = request.headers.get('x-auth-token')
            # Recover OV connection
            oneview_client = util.get_oneview_client(session_id)
        else:
            oneview_client = util.get_oneview_client()

        server_hardware = oneview_client.server_hardware. \
            get(uuid)

        sht_uri = server_hardware['serverHardwareTypeUri']
        server_hardware_type = \
            oneview_client.server_hardware_types.get(sht_uri)

        st = Storage(uuid, server_hardware_type)

        json_str = st.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            if e.msg.find("server-hardware-types") >= 0:
                logging.warning(
                    'Server hardware type ID {} not found'.
                    format(server_hardware['serverHardwareTypeUri']))
                abort(
                    status.HTTP_404_NOT_FOUND,
                    "Server hardware types not found")
            else:
                logging.warning(
                    'Server hardware UUID {} not found'.
                    format(uuid))
                abort(
                    status.HTTP_404_NOT_FOUND,
                    "Server hardware not found")
        elif e.msg.find("server-hardware-types") >= 0:
            logging.exception(
                'OneView Exception while looking for server hardware type'
                ' {}'.format(e)
            )
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
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
