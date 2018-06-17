# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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

import logging

from flask import abort
from flask import Blueprint
from flask import g
from flask import Response
from flask_api import status

from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.resource_block_computer_system \
    import ResourceBlockComputerSystem
from oneview_redfish_toolkit.api.server_hardware_resource_block \
    import ServerHardwareResourceBlock


RESOURCE_BLOCK_URI = "/redfish/v1/CompositionService/ResourceBlocks"

resource_block = Blueprint("resource_block", __name__)


@resource_block.route(RESOURCE_BLOCK_URI + "/<uuid>", methods=["GET"])
def get_resource_block(uuid):
    """Get the Redfish ResourceBlock for a given UUID.

        Return ResourceBlock redfish JSON for a given UUID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock.
    """

    try:
        resource_index = g.oneview_client.index_resources.get_all(
            filter='uuid=' + uuid
        )

        if resource_index:
            category = resource_index[0]["category"]
        else:
            raise OneViewRedfishError('Cannot find resource')

        if category == 'server-hardware':
            # Get server hardware for given UUID
            server_hardware = g.oneview_client.server_hardware.get(uuid)

            eTag = server_hardware['eTag']
            eg_uri = server_hardware["serverGroupUri"]
            sht_uri = server_hardware["serverHardwareTypeUri"]

            filters = list()
            filters.append("enclosureGroupUri='{}'".format(eg_uri))
            filters.append("serverHardwareTypeUri='{}'".format(sht_uri))

            server_profile_templates = g.oneview_client \
                .server_profile_templates.get_all(filter=filters)

            # Build ResourceBlock object and validates it
            resource_block = ServerHardwareResourceBlock(
                uuid, server_hardware, server_profile_templates)
        else:
            raise OneViewRedfishError('Resource block type not found')

        # Build redfish json
        json_str = resource_block.serialize()

        # Build response and returns
        response = Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
        response.headers.add("ETag", "W/" + eTag)

        return response
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)
        abort(status.HTTP_404_NOT_FOUND, "Resource block not found")

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)

    except Exception as e:
        # In case of error print exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@resource_block.route(
    RESOURCE_BLOCK_URI + "/<uuid>/Systems/<serial>", methods=["GET"])
def get_resource_block_computer_system(uuid, serial):
    """Get Computer System of a Resource Block

        Return ResourceBlock Computer System redfish JSON for a given
        UUID and serial number. Logs exception of any error and return
        Internal Server Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlock Computer System.
    """

    try:
        server_hardware = g.oneview_client.server_hardware.get(uuid)

        if server_hardware["serialNumber"] != serial:
            raise OneViewRedfishError(
                "Computer system of resource block {} not found".format(uuid))

        computer_system = ResourceBlockComputerSystem(server_hardware)

        json_str = computer_system.serialize()

        response = Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
        response.headers.add("ETag", "W/" + server_hardware["eTag"])
        return response
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)
        abort(status.HTTP_404_NOT_FOUND,
              "Computer system of resource block not found")

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)

    except Exception as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
