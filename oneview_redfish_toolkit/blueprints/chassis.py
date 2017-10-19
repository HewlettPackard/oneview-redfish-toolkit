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
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Own libs
from oneview_redfish_toolkit.api.blade_chassis import BladeChassis
from oneview_redfish_toolkit.api.enclosure_chassis import EnclosureChassis
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.rack_chassis import RackChassis
from oneview_redfish_toolkit import util

chassis = Blueprint("chassis", __name__)


@chassis.route("/redfish/v1/Chassis/<uuid>/", methods=["GET"],
               strict_slashes=False)
def get_chassis(uuid):
    """Get the Redfish Chassis.

        Get method to return Chassis JSON when
        /redfish/v1/Chassis/id is requested.

        Returns:
            JSON: JSON with Chassis.
    """
    try:
        oneview_client = util.get_oneview_client()

        resource_index = oneview_client.index_resources.get_all(
            filter='uuid=' + uuid
        )

        if resource_index:
            category = resource_index[0]["category"]
        else:
            raise OneViewRedfishError('Cannot find Index resource')

        if category == 'server-hardware':
            server_hardware = oneview_client.server_hardware.get(uuid)
            ch = BladeChassis(server_hardware)
        elif category == 'enclosures':
            enclosure = oneview_client.enclosures.get(uuid)
            enclosure_environment_config = oneview_client.enclosures.\
                get_environmental_configuration(uuid)
            ch = EnclosureChassis(
                enclosure,
                enclosure_environment_config
            )
        elif category == 'racks':
            racks = oneview_client.racks.get(uuid)
            ch = RackChassis(racks)
        else:
            raise OneViewRedfishError('Chassis type not found')

        json_str = ch.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.error(e)
        abort(status.HTTP_404_NOT_FOUND)

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, "Chassis not found")

    except Exception as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
