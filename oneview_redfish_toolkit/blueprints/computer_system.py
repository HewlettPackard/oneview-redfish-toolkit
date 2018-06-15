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
from flask import request
from flask import Response
from flask_api import status

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import OneViewRedfishError


computer_system = Blueprint("computer_system", __name__)


@computer_system.route("/redfish/v1/Systems/<uuid>", methods=["GET"])
def get_computer_system(uuid):
    """Get the Redfish Computer System for a given UUID.

        Return ComputerSystem redfish JSON for a given
        server hardware UUID.
        Logs exception of any error and return abort(500)
        Internal Server Error.

        Returns:
            JSON: Redfish json with ComputerSystem
            When Server hardware is not found calls abort(404)

        Exceptions:
            Logs the exception and call abort(500)
    """
    try:
        # Gets server hardware for given UUID
        server_hardware = g.oneview_client.server_hardware.get(uuid)

        # Gets the server hardware type of the given server hardware
        server_hardware_types = g.oneview_client.server_hardware_types.get(
            server_hardware['serverHardwareTypeUri']
        )

        # Build Computer System object and validates it
        cs = ComputerSystem(server_hardware, server_hardware_types)

        # Build redfish json
        json_str = cs.serialize()

        # Build response and returns
        response = Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
        response.headers.add("ETag", "W/" + server_hardware['eTag'])
        return response
    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            if e.msg.find("server-hardware-types") >= 0:
                logging.warning(
                    'ServerHardwareTypes ID {} not found'.
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


@computer_system.route("/redfish/v1/Systems/<uuid>/"
                       "Actions/ComputerSystem.Reset", methods=["POST"])
def change_power_state(uuid):
    """Change the Oneview power state for a specific Server hardware.

        Return ResetType Computer System redfish JSON for a
        given server hardware UUID.
        Logs exception of any error and return abort.

        Returns:
            JSON: Redfish JSON with ComputerSystem ResetType.

        Exceptions:
            HPOneViewException: When some OneView resource was not found.
            return abort(404)

            OneViewRedfishError: When occur a power state mapping error.
            return abort(400)

            Exception: Unexpected error.
            return abort(500)
    """

    try:
        try:
            reset_type = request.get_json()["ResetType"]
        except Exception:
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key"})

        # Gets ServerHardware for given UUID
        sh = g.oneview_client.server_hardware.get(uuid)

        # Gets the ServerHardwareType of the given server hardware
        sht = g.oneview_client.server_hardware_types. \
            get(sh['serverHardwareTypeUri'])

        # Build Computer System object and validates it
        cs = ComputerSystem(sh, sht)

        oneview_power_configuration = \
            cs.get_oneview_power_configuration(reset_type)

        # Changes the ServerHardware power state
        g.oneview_client.server_hardware.update_power_state(
            oneview_power_configuration, uuid)

        return Response(
            response='{"ResetType": "%s"}' % reset_type,
            status=status.HTTP_200_OK,
            mimetype='application/json')

    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)

        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            abort(status.HTTP_404_NOT_FOUND, "Server hardware not found")
        else:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Mapping error: {}'.format(e))

        if e.msg["errorCode"] == "NOT_IMPLEMENTED":
            abort(status.HTTP_501_NOT_IMPLEMENTED, e.msg['message'])
        else:
            abort(status.HTTP_400_BAD_REQUEST, e.msg['message'])

    except Exception as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@computer_system.route(
    "/redfish/v1/Systems/<uuid>", methods=["DELETE"])
def remove_subscription(uuid):
    """Removes a specific System

        Args:
            uuid: The System ID.
    """
    try:
        # Deletes server profile for given UUID
        sucess = g.oneview_client.server_profiles.delete(uuid)

        if not sucess:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)

        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            abort(status.HTTP_404_NOT_FOUND, "Computer Sytem not found")
        else:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
