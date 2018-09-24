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

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.thermal import Thermal
from oneview_redfish_toolkit import category_resource


thermal = Blueprint("thermal", __name__)


@thermal.route("/redfish/v1/Chassis/<uuid>/Thermal", methods=["GET"])
def get_thermal(uuid):
    """Get the Redfish Thermal for a given UUID.

        Return Thermal Redfish JSON for a given hardware UUID.
        Logs exception of any error and return abort(500)
        Internal Server Error.

        Returns:
            JSON: Redfish json with Thermal
            When hardware is not found calls abort(404)

        Exceptions:
            Logs the exception and call abort(500)

    """
    try:
        category = ''
        cached_category = category_resource.get_category_by_resource_id(uuid)

        if cached_category:
            category = cached_category.resource.replace('_', '-')
        else:
            index_obj = g.oneview_client.index_resources.get_all(
                filter='uuid=' + uuid
            )

            if index_obj:
                category = index_obj[0]["category"]
            else:
                raise OneViewRedfishError('Cannot find Index resource')

        if category == 'server-hardware':
            server_hardware = g.oneview_client.server_hardware. \
                get_utilization(uuid, fields='AmbientTemperature')
            thrml = Thermal(server_hardware, uuid, 'Blade')
        elif category == 'enclosures':
            enclosure = g.oneview_client.enclosures. \
                get_utilization(uuid, fields='AmbientTemperature')
            thrml = Thermal(enclosure, uuid, 'Enclosure')
        elif category == 'racks':
            rack = g.oneview_client.racks.\
                get_device_topology(uuid)
            thrml = Thermal(rack, uuid, 'Rack')
        else:
            raise OneViewRedfishError('OneView resource not found')

        json_str = thrml.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        # In case of error print exception and abort
        logging.exception(e)

        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            abort(status.HTTP_404_NOT_FOUND, "Resource not found")
        else:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    except OneViewRedfishError as e:
        # In case of error print exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, "Resource not found")

    except Exception as e:
        # In case of error print exception and abort
        logging.exception(e)
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
