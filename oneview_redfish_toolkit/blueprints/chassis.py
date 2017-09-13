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

# Own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.chassis import Chassis
from oneview_redfish_toolkit import util

chassis = Blueprint("chassis", __name__)


@chassis.route("/redfish/v1/Chassis/<uuid>", methods=["GET"])
def get_chassis(uuid):
    """Get the Redfish Chassis.

        Get method to return Chassis JSON when
        /redfish/v1/Chassis/id is requested.

        Returns:
            JSON: JSON with Chassis.
    """
    try:
        ov_client = util.get_oneview_client()

        index_obj = ov_client.index_resources.get_all(filter='uuid=' + uuid)
        category = index_obj[0]["category"]

        if category == 'server-hardware':
            ov_sh = ov_client.server_hardware.get(uuid)
            ch = Chassis(ov_sh)
        elif category == 'enclosures':
            # ov_encl = ov_client.enclosures.get(uuid)
            # ch = Chassis(ov_encl)
            abort(500)
        elif category == 'racks':
            # ov_racks = ov_client.racks.get(uuid)
            # ch = Chassis(ov_racks)
            abort(500)
        else:
            abort(404)

        json_str = ch.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        # In case of error print exception and abort
        logging.error(e)
        abort(status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # In case of error print exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@chassis.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    return Response(
        response='{"error": "URL/data not found"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@chassis.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates an Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype='application/json')
