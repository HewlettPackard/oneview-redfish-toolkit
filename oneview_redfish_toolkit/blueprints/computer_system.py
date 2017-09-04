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
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit import util


computer_system = Blueprint("computer_system", __name__)


@computer_system.route("/redfish/v1/Systems/<uuid>", methods=["GET"])
def get_computer_system(uuid):
    """Get the Redfish Computer System for a given UUDI.

        Return ComputerSystem redfish JSON for a given
        server harder UUID.
        Logs exception of any error and return abort(500)
        Internal Server Error.

        Returns:
            JSON: Redfish json with ComputerSystem
            When Server hardware is not found calls abort(404)


        Exceptions:
            Logs the exception and call abort(500)

    """
    try:
        # Recover OV connection
        ov_client = util.get_oneview_client()

        # Gets serverhardware for given UUID
        sh = ov_client.server_hardware.get(uuid)

        # Gets de server hardware type of the given server hardware
        sht = ov_client.server_hardware_types.get(sh['serverHardwareTypeUri'])

        # Build Computer System object and validates it
        cs = ComputerSystem(sh, sht)

        # Build redfish json
        json_str = cs.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        if e.error_code == "RESOURCE_NOT_FOUND":
            if e.msg.find("server-hardware-types") >= 0:
                logging.warning(
                    'ServerHardwareTypes ID {} not found'.
                    format(sh['serverHardwareTypeUri']))
            else:
                logging.warning(
                    'ServerHardware UUID {} not found'.
                    format(uuid))
            abort(status.HTTP_404_NOT_FOUND)
        elif e.msg.find("server-hardware-types") >= 0:
            logging.error(
                'OneView Exception while looking for server hardware type'
                ' {}'.format(e)
            )
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif e.msg.find("server-hardware") >= 0:
            logging.error(
                'OneView Exception while looking for '
                'server hardware: {}'.format(e)
            )
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logging.error('Unexpected OneView Exception: {}'.format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # In case of error print exception and abort
        logging.error('Unexepected error: '.format(e))
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@computer_system.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    return Response(
        response={'error': 'URL not found'},
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@computer_system.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates an Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response={'error': 'Internal Server Error'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype='application/json')
