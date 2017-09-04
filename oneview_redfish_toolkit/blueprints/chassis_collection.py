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

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.chassis_collection import ChassisCollection
from oneview_redfish_toolkit import util


chassis_collection = Blueprint("chassis_collection", __name__)


@chassis_collection.route("/redfish/v1/Chassis/", methods=["GET"])
def get_chassis_collection():
    """Get the Redfish Chassis Collection.

        Return ChassisCollection redfish JSON.
        Logs exception of any error and return
        Internal Server Error or Not Found.

        Returns:
            JSON: Redfish json with ChassisCollection.
            When Server hardwares, enclosures or racks is not found
            calls abort(404).

        Exceptions:
            HPOneViewException: if have some error with gets of
            Oneview Resources (ServerHardware, Enclosures or Racks).
            Exception: Generic error, logs the exception and call abort(500).
    """

    try:
        # Recover OV connection
        ov_client = util.get_oneview_client()

        # Gets all enclosures
        oneview_enclosures = ov_client.enclosures.get_all()

        # Gets all racks
        oneview_racks = ov_client.racks.get_all()

        # Gets all server hardware
        oneview_server_hardwares = ov_client.server_hardware.get_all()

        # Build Chassis Collection object and validates it
        cc = ChassisCollection(oneview_server_hardwares, oneview_enclosures,
                               oneview_racks)

        # Build redfish json
        json_str = cc.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")

    except HPOneViewException as e:
        if e.error_code == "RESOURCE_NOT_FOUND":
            if e.msg.find("server-hardwares") >= 0:
                logging.warning('ServerHardwares not found.')
            elif e.msg.find("enclosures") >= 0:
                logging.warning('Enclosures not found.')
            else:
                logging.warning('Racks not found.')

            abort(status.HTTP_404_NOT_FOUND)

        elif e.msg.find("server-hardwares") >= 0:
            logging.error(
                'OneView Exception while looking for server hardwares'
                ' {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif e.msg.find("enclosures") >= 0:
            logging.error(
                'OneView Exception while looking for '
                'enclosure: {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif e.msg.find("racks") >= 0:
            logging.error(
                'OneView Exception while looking for '
                'racks: {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logging.error('Unexpected OneView Exception: {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        # In case of error print exception and abort
        logging.error('Unexpected error: '.format(e))
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@chassis_collection.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "URL not found"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@chassis_collection.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates a Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype="application/json")
