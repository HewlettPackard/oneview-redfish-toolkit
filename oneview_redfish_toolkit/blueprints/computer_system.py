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
from functools import reduce
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
from hpOneView.exceptions import HPOneViewTaskError

from hpOneView.resources.task_monitor import TASK_ERROR_STATES
from jsonschema import ValidationError

from oneview_redfish_toolkit.api.capabilities_object import CapabilitiesObject
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.util.power_option import OneViewPowerOption
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit.services.computer_system_service import \
    ComputerSystemService
from oneview_redfish_toolkit.services.manager_service import \
    get_manager_uuid
from oneview_redfish_toolkit.single_oneview_context import single_oneview

computer_system = Blueprint("computer_system", __name__)


@computer_system.route("/redfish/v1/Systems/<uuid>", methods=["GET"])
@single_oneview
def get_computer_system(uuid):
    """Get the Redfish Computer System for a given UUID.

        Return ComputerSystem redfish JSON for a given
        server profile or server profile template UUID.

        Returns:
            JSON: Redfish json with ComputerSystem
            When Server hardware or Server profilte templates
            is not found calls abort(404)
    """

    resource = _get_oneview_resource(uuid)
    category = resource["category"]

    if category == 'server-profile-templates':
        computer_system_resource = CapabilitiesObject(resource)
    elif category == 'server-profiles':
        server_hardware = g.oneview_client.server_hardware\
            .get_by_uri(resource["serverHardwareUri"]).data
        server_hardware_type = g.oneview_client.server_hardware_types\
            .get_by_uri(resource['serverHardwareTypeUri']).data

        computer_system_service = ComputerSystemService(g.oneview_client)
        drives = _get_drives_from_sp(resource)
        spt_uuid = computer_system_service.\
            get_server_profile_template_from_sp(resource["uri"])

        # Get external storage volumes from server profile
        volumes_uris = [volume["volumeUri"] for volume in resource[
            "sanStorage"]["volumeAttachments"]]

        # Emptying volume list to suppress external storage changes for
        # current release.
        # In future, remove this line to enable external storage support
        volumes_uris = []

        manager_uuid = get_manager_uuid(resource['serverHardwareTypeUri'])

        # Build Computer System object and validates it
        computer_system_resource = ComputerSystem.build_composed_system(
            server_hardware,
            server_hardware_type,
            resource,
            drives,
            spt_uuid,
            manager_uuid,
            volumes_uris)
    else:
        abort(status.HTTP_404_NOT_FOUND,
              'Computer System UUID {} not found'.format(uuid))

    return ResponseBuilder.success(
        computer_system_resource,
        {"ETag": "W/" + resource["eTag"]})


@computer_system.route("/redfish/v1/Systems/<uuid>/"
                       "Actions/ComputerSystem.Reset", methods=["POST"])
def change_power_state(uuid):
    """Change the Oneview power state for a specific Server hardware.

        Return ResetType Computer System redfish JSON for a
        given server profile UUID.
        Logs exception of any error and return abort.

        Returns:
            JSON: Redfish JSON with ComputerSystem ResetType.
    """

    try:
        reset_type = request.get_json()["ResetType"]
    except KeyError:
        invalid_key = list(request.get_json())[0]  # gets invalid key name
        abort(status.HTTP_400_BAD_REQUEST,
              "Invalid JSON key: {}".format(invalid_key))

    # Gets ServerHardware for given UUID
    profile = g.oneview_client.server_profiles.get_by_id(uuid).data
    sh = g.oneview_client.server_hardware.get_by_uri(
        profile["serverHardwareUri"]).data

    oneview_power_configuration = \
        OneViewPowerOption.get_oneview_power_configuration(
            sh, reset_type)

    # Changes the ServerHardware power state
    g.oneview_client.server_hardware.update_power_state(
        oneview_power_configuration, sh["uuid"])

    return Response(
        response='{"ResetType": "%s"}' % reset_type,
        status=status.HTTP_200_OK,
        mimetype='application/json')


@computer_system.route(
    "/redfish/v1/Systems/<uuid>", methods=["DELETE"])
def remove_computer_system(uuid):
    """Removes a specific System

        Args:
            uuid: The System ID.
    """
    try:
        profile = g.oneview_client.server_profiles.get_by_id(uuid).data
    except HPOneViewException as e:
        abort(status.HTTP_404_NOT_FOUND, e.msg)

    sh_uuid = profile['serverHardwareUri']
    if sh_uuid:
        service = ComputerSystemService(g.oneview_client)
        service.power_off_server_hardware(sh_uuid)

    # Deletes server profile for given UUID
    response = None
    try:
        response = g.oneview_client.server_profiles.delete(uuid)
    except HPOneViewTaskError as e:
        abort(status.HTTP_403_FORBIDDEN, e.msg)

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


@computer_system.route(ComputerSystem.BASE_URI + "/", methods=["POST"])
def create_composed_system():
    if not request.is_json:
        abort(status.HTTP_400_BAD_REQUEST,
              "The request content should be a valid JSON")

    body = request.get_json()

    result_location_uri = None

    try:
        RedfishJsonValidator.validate(body, 'ComputerSystem')
        service = ComputerSystemService(g.oneview_client)

        blocks = body["Links"]["ResourceBlocks"]
        block_ids = [block["@odata.id"].split("/")[-1] for block in blocks]

        # Should contain only one computer system entry
        system_blocks = _get_system_resource_blocks(block_ids)
        if not system_blocks:
            raise ValidationError(
                "Should have a Computer System Resource Block")

        system_block = system_blocks[0]
        service.validate_computer_system_resource_block_to_composition(
            system_block)

        # Check network block id with the Id attribute in the request
        network_blocks = _get_network_resource_blocks(block_ids)
        spt_id = body["Id"]

        if not (network_blocks and spt_id in network_blocks[0]["uri"]):
            raise ValidationError(
                "Should have a valid Network Resource Block")

        # It can contain zero or more Storage Block
        storage_blocks = _get_storage_resource_blocks(block_ids)

        spt = g.oneview_client.server_profile_templates.get_by_id(spt_id).data

        # Check for external storage block.
        external_storage_blocks = _get_external_storage_block(block_ids)
        if external_storage_blocks:
            is_fibre_channel_nw = _get_fibre_channel_network(spt)
            if is_fibre_channel_nw:
                for volume in external_storage_blocks:
                    storage_pool = g.oneview_client.storage_pools.get_by_uri(
                        volume["storagePoolUri"]).data
                    if storage_pool:
                        storage_system_uri = storage_pool["storageSystemUri"]
                        volume["storageSystemUri"] = storage_system_uri
            else:
                raise ValidationError(
                    "Should have a Fibre Channel Network Connection")

        server_profile = ComputerSystem.build_server_profile(
            body["Name"],
            body.get("Description"),
            spt,
            system_block,
            network_blocks,
            storage_blocks,
            external_storage_blocks)

        service.power_off_server_hardware(system_block["uuid"],
                                          on_compose=True)

        task, resource_uri = service.create_composed_system(server_profile)

        if resource_uri:
            result_uuid = resource_uri.split("/")[-1]
            result_location_uri = ComputerSystem.BASE_URI + "/" + result_uuid
            server_profile_label = dict(
                resourceUri=resource_uri, labels=[spt_id.replace("-", " ")])
            g.oneview_client.labels.create(server_profile_label)
        elif task.get("taskErrors"):
            err_msg = reduce(
                lambda result, msg: result + msg["message"] + "\n",
                task["taskErrors"],
                "")
            abort(status.HTTP_403_FORBIDDEN, err_msg)

    except ValidationError as e:
        abort(status.HTTP_400_BAD_REQUEST, e.message)
    except KeyError as e:
        abort(status.HTTP_400_BAD_REQUEST,
              "Trying access an invalid key {}".format(e.args))
    except HPOneViewTaskError as e:
        abort(status.HTTP_403_FORBIDDEN, e.msg)

    if not result_location_uri:
        logging.error("It was not possible get the server profile URI when "
                      "creating a composed system")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_201_CREATED,
                    headers={"Location": result_location_uri},
                    mimetype="application/json")


def _get_oneview_resource(uuid):
    """Gets a Server hardware or Server profile templates"""
    cached_category = category_resource.get_category_by_resource_id(uuid)

    if cached_category:
        resource = getattr(g.oneview_client, cached_category.resource)
        function = getattr(resource, cached_category.function)
        result = function(uuid)
        if isinstance(result, dict):
            return result
        else:
            return result.data

    categories = [
        {"func": g.oneview_client.server_profiles.get_by_id, "param": uuid},
        {"func": g.oneview_client.server_profile_templates.get_by_id, "param": uuid}
    ]

    for category in categories:
        try:
            resource = category["func"](category["param"])
            if isinstance(resource, dict):
                return resource
            return resource.data

        except HPOneViewException as e:
            if e.oneview_response["errorCode"] in \
                    ['RESOURCE_NOT_FOUND', 'ProfileNotFoundException']:
                pass
            else:
                raise  # Raise any unexpected errors

    abort(status.HTTP_404_NOT_FOUND,
          "Could not find computer system with id " + uuid)


def _get_system_resource_blocks(ids):
    return _get_resource_block_data(
        g.oneview_client.server_hardware.get_by_id, ids)


def _get_network_resource_blocks(ids):
    return _get_resource_block_data(
        g.oneview_client.server_profile_templates.get_by_id, ids)


def _get_storage_resource_blocks(ids):
    drive_ids = ["/rest/drives/" + i for i in ids]

    return _get_resource_block_data(
        g.oneview_client.index_resources.get, drive_ids)


def _get_external_storage_block(ids):
    return _get_resource_block_data(
        g.oneview_client.volumes.get_by_id, ids)


def _get_fibre_channel_network(spt):
    is_fibre_channel_nw = False
    for connection in spt["connectionSettings"]["connections"]:
        if connection["functionType"] == "FibreChannel":
            is_fibre_channel_nw = True
            break
    return is_fibre_channel_nw


def _get_resource_block_data(func, uuids):
    resources = list()

    for uuid in uuids:
        try:
            resource = func(uuid)
            if isinstance(resource, dict):
                resources.append(resource)
            else:
                resources.append(resource.data)

        except HPOneViewException as e:
            # With our current implementation, we do not getting
            # server_profile, but if we need get it in some moment,
            # we must check the errorCode 'ProfileNotFoundException'
            if e.oneview_response["errorCode"] == 'RESOURCE_NOT_FOUND':
                pass
            else:
                raise  # Raise any unexpected errors

    return resources


def _get_drives_from_sp(server_profile):
    """Gets Drives from Server Profile"""
    jbods_drives = list()
    for sas_logical_jbod in server_profile["localStorage"]["sasLogicalJBODs"]:
        if sas_logical_jbod["sasLogicalJBODUri"]:
            drives_by_sas_logical_uuid = g.oneview_client.sas_logical_jbods. \
                get_drives(sas_logical_jbod["sasLogicalJBODUri"])
            jbods_drives.extend(drives_by_sas_logical_uuid)

    return jbods_drives
