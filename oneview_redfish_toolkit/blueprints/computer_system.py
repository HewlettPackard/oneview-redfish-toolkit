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
from hpOneView.resources.task_monitor import TASK_ERROR_STATES
from oneview_redfish_toolkit.api.capabilities_object import CapabilitiesObject
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import OneViewRedfishError


computer_system = Blueprint("computer_system", __name__)


@computer_system.route("/redfish/v1/Systems/<uuid>", methods=["GET"])
def get_computer_system(uuid):
    """Get the Redfish Computer System for a given UUID.

        Return ComputerSystem redfish JSON for a given
        server hardware or server profile templates UUID.
        Logs exception of OneViewRedfishError and abort(404).

        Returns:
            JSON: Redfish json with ComputerSystem
            When Server hardware or Server profilte templates
            is not found calls abort(404)
    """

    try:
        resource = _get_oneview_resource(uuid)
        category = resource["category"]
        headers = ()

        if category == 'server-hardware':
            cs = _build_computer_system_server_hardware(resource)
            headers = ("ETag", "W/" + resource['eTag'])
        elif category == 'server-profile-templates':
            cs = CapabilitiesObject(resource)
        else:
            raise OneViewRedfishError('Computer System type not found')

        # Build redfish json
        json_str = cs.serialize()

        # Build response and returns
        response = Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")

        if headers:
            response.headers.add(*headers)

        return response
    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)


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
def remove_computer_system(uuid):
    """Removes a specific System

        Args:
            uuid: The System ID.
    """
    # Deletes server profile for given UUID
    response = g.oneview_client.server_profiles.delete(uuid)

    if response is True:
        return Response(status=status.HTTP_204_NO_CONTENT,
                        mimetype="application/json")

    # Check if returned a task
    if type(response) is dict:
        # Check if task is completed
        if response['taskState'] == 'Completed':
            return Response(status=status.HTTP_204_NO_CONTENT,
                            mimetype="application/json")

        # Log task error messages if it has
        if response['taskState'] in TASK_ERROR_STATES and \
            'taskErrors' in response and len(response['taskErrors']) > 0:
            for err in response['taskErrors']:
                if 'message' in err:
                    logging.exception(err['message'])

    abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_oneview_resource(uuid):
    """Gets a Server hardware or Server profile templates"""
    categories = [
        {"func": g.oneview_client.server_hardware.get, "param": uuid},
        {"func": g.oneview_client.server_profile_templates.get, "param": uuid},
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

    raise OneViewRedfishError("Could not find computer system with id " + uuid)


def _build_computer_system_server_hardware(server_hardware):
    try:
        # Gets the server hardware type of the given server hardware
        server_hardware_types = g.oneview_client.server_hardware_types.get(
            server_hardware['serverHardwareTypeUri']
        )

        # Build Computer System object and validates it
        return ComputerSystem(server_hardware, server_hardware_types)
    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            raise OneViewRedfishError(
                'ServerHardwareTypes ID {} not found'.
                format(server_hardware['serverHardwareTypeUri']))

        raise e
