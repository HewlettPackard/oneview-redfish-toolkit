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
import json

# 3rd party libs
from copy import deepcopy
from flask import abort
from flask import Blueprint
from flask import g
from flask import request
from flask import Response
from flask_api import status
from jsonschema import ValidationError

# own libs
from hpOneView.exceptions import HPOneViewException
from hpOneView.resources.task_monitor import TASK_ERROR_STATES
from oneview_redfish_toolkit.api.capabilities_object import CapabilitiesObject
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.util.power_option import OneViewPowerOption
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

STORAGE_TEMPLATE = {
    "id": None, # Numeric (int)
    "deviceSlot": None, # String
    "name": None, # String
    "numPhysicalDrives": 1,
    "driveMinSizeGB": None, # Numeric (int)
    "driveMaxSizeGB": None, # Numeric (int)
    "driveTechnology": None, # String
}

computer_system = Blueprint("computer_system", __name__)


@computer_system.route("/redfish/v1/Systems/<uuid>", methods=["GET"])
def get_computer_system(uuid):
    """Get the Redfish Computer System for a given UUID.

        Return ComputerSystem redfish JSON for a given
        server profile or server profile template UUID.
        Logs exception of OneViewRedfishError and abort(404).

        Returns:
            JSON: Redfish json with ComputerSystem
            When Server hardware or Server profilte templates
            is not found calls abort(404)
    """

    try:
        resource = _get_oneview_resource(uuid)
        category = resource["category"]

        if category == 'server-profile-templates':
            computer_system = CapabilitiesObject(resource)
        elif category == 'server-profiles':
            server_hardware = g.oneview_client.server_hardware\
                .get(resource["serverHardwareUri"])
            server_hardware_type = g.oneview_client.server_hardware_types\
                .get(resource['serverHardwareTypeUri'])

            # Build Computer System object and validates it
            computer_system = ComputerSystem(server_hardware,
                                             server_hardware_type,
                                             resource)
        else:
            raise OneViewRedfishError(
                'Computer System UUID {} not found'.format(uuid))

        return ResponseBuilder.success(
            computer_system,
            {"ETag": "W/" + resource["eTag"]})
    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)


@computer_system.route("/redfish/v1/Systems/<uuid>/"
                       "Actions/ComputerSystem.Reset", methods=["POST"])
def change_power_state(uuid):
    """Change the Oneview power state for a specific Server hardware.

        Return ResetType Computer System redfish JSON for a
        given server profile UUID.
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
        except KeyError:
            invalid_key = list(request.get_json())[0]  # gets invalid key name
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key: {}".format(invalid_key)})

        # Gets ServerHardware for given UUID
        profile = g.oneview_client.server_profiles.get(uuid)
        sh = g.oneview_client.server_hardware.get(profile["serverHardwareUri"])

        # Gets the ServerHardwareType of the given server hardware
        sht = g.oneview_client.server_hardware_types. \
            get(profile["serverHardwareTypeUri"])

        # Build Computer System object and validates it
        cs = ComputerSystem(sh, sht, profile)

        oneview_power_configuration = \
            OneViewPowerOption.get_oneview_power_configuration(
                cs.server_hardware, reset_type)

        # Changes the ServerHardware power state
        g.oneview_client.server_hardware.update_power_state(
            oneview_power_configuration, sh["uuid"])

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
        {"func": g.oneview_client.server_profiles.get, "param": uuid},
        {"func": g.oneview_client.server_profile_templates.get, "param": uuid}
    ]

    for category in categories:
        try:
            resource = category["func"](category["param"])

            return resource
        except HPOneViewException as e:
            if e.oneview_response["errorCode"] in \
                    ['RESOURCE_NOT_FOUND', 'ProfileNotFoundException']:
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


@computer_system.route("/redfish/v1/Systems/", methods=["POST"])
def create_composed_system():
    if not request.is_json:
        abort(status.HTTP_400_BAD_REQUEST)

    body = request.get_json()

    class ComposedSystem(RedfishJsonValidator):
        SCHEMA_NAME = 'ComputerSystem'

        def __init__(self, composed_system):
            super().__init__(self.SCHEMA_NAME)

            self.redfish = composed_system

        def validate(self):
            self._validate()

    try:
        resource = ComposedSystem(body)
        resource.validate()

        blocks = resource.redfish["Links"]["ResourceBlocks"]
        block_ids = \
            list(map(lambda b: b["@odata.id"].split("/")[-1], blocks))

        # Should contain only one computer system entry
        system_blocks = _get_system_resource_blocks(block_ids)
        # Check network block id with the Id attribute in the request
        network_blocks = _get_network_resource_blocks(block_ids)
        # Check which disks are available ('available' attribute)
        storage_blocks = _get_storage_resource_blocks(block_ids)

        spt = g.oneview_client.server_profile_templates.get(body["Id"])

        server_profile = _build_server_profile(
            spt, system_blocks, network_blocks, storage_blocks)

        print(json.dumps(server_profile))

    except ValidationError as e:
        abort(status.HTTP_400_BAD_REQUEST, e.message)
    except KeyError:
        abort(status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


def _build_server_profile(spt, system_blocks, network_blocks, storage_blocks):
    server_profile = deepcopy(spt)

    # Remove attributes
    del server_profile["uri"]
    del server_profile["serverProfileDescription"]
    del server_profile["created"]
    del server_profile["modified"]
    del server_profile["status"]
    del server_profile["state"]
    del server_profile["scopesUri"]
    del server_profile["eTag"]
    del server_profile["connectionSettings"]["manageConnections"]

    # Set attributes with different value
    server_profile["type"] = "ServerProfileV8"
    server_profile["category"] = "server-profiles"
    server_profile["serverHardwareUri"] = \
        "/rest/server-hardware/" + system_blocks[0]["uuid"]

    # Configure storage
    controller = _get_storage_controller(spt)

    storage_id = 1

    for storage_block in storage_blocks:
        storage = dict()

        storage["id"] = storage_id
        storage["name"] = "Storage " + storage_id
        storage["deviceSlot"] = controller["deviceSlot"]
        storage["numPhysicalDrives"] = 1,
        storage["driveMinSizeGB"] = storage_block["capacityInGB"]
        storage["driveMaxSizeGB"] = storage_block["capacityInGB"]
        storage["driveTechnology"] = \
            storage_block["interfaceType"].capitalize() \
            + storage_block["mediaType"].capitalize()

        storage_id += 1

        server_profile["localStorage"]["sasLogicalJBODs"].append(storage)

    return server_profile

def _get_storage_controller(server_profile_template):
    for controller in server_profile_template["localStorage"]["controllers"]:
        if controller["deviceSlot"] != "Embedded":
            return controller

    return None


def _get_system_resource_blocks(ids):
    return _get_resource_block_data(
        g.oneview_client.server_hardware.get, ids)


def _get_network_resource_blocks(ids):
    return _get_resource_block_data(
        g.oneview_client.server_profile_templates.get, ids)


def _get_storage_resource_blocks(ids):
    drive_ids = list(map(lambda v: "/rest/drives/" + v, ids))

    return _get_resource_block_data(
        g.oneview_client.index_resources.get, drive_ids)


def _get_resource_block_data(func, uuids):
    resources = list()

    for uuid in uuids:
        try:
            resource = func(uuid)

            resources.append(resource)
        except HPOneViewException as e:
            if e.oneview_response["errorCode"] == 'RESOURCE_NOT_FOUND':
                pass
            else:
                raise  # Raise any unexpected errors

    return resources
