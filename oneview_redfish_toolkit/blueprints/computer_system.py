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
from flask import request
from flask import Response
from flask_api import status

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import util


computer_system = Blueprint("computer_system", __name__, url_prefix="/redfish/v1/Systems/")


@computer_system.route("<uuid>", methods=["GET"])
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
        # Recover OV connection
        ov_client = util.get_oneview_client()

        # Gets serverhardware for given UUID
        sh = ov_client.server_hardware.get(uuid)

        # Gets the server hardware type of the given server hardware
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
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
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


@computer_system.route("<uuid>/Actions/ComputerSystem.Reset", methods=["POST"])
def change_power_state(uuid):
    reset_type = request.form["ResetType"]

    reset_type_dict = dict()

    reset_type_dict["On"] = dict()
    reset_type_dict["On"]["powerState"] = "On"
    reset_type_dict["On"]["powerControl"] = "MomentaryPress"

    reset_type_dict["ForceOff"] = dict()
    reset_type_dict["ForceOff"]["powerState"] = "Off"
    reset_type_dict["ForceOff"]["powerControl"] = "PressAndHold"

    reset_type_dict["GracefulShutdown"] = dict()
    reset_type_dict["GracefulShutdown"]["powerState"] = "Off"
    reset_type_dict["GracefulShutdown"]["powerControl"] = "MomentaryPress"

    reset_type_dict["GracefulRestart"] = dict()
    reset_type_dict["GracefulRestart"]["powerState"] = "On"
    reset_type_dict["GracefulRestart"]["powerControl"] = "Reset"

    reset_type_dict["ForceRestart"] = dict()
    reset_type_dict["ForceRestart"]["powerState"] = "On"
    reset_type_dict["ForceRestart"]["powerControl"] = "ColdBoot"

    reset_type_dict["PushPowerButton"] = dict()
    reset_type_dict["PushPowerButton"]["powerControl"] = "MomentaryPress"

    try:

        try:
            new_state = reset_type_dict[reset_type]
        except Exception:
            raise OneViewRedfishError(
                'There is no mapping for {} on the OneView'.format(reset_type)
            )

        ov_client = util.get_oneview_client()

        if reset_type == "PushPowerButton":
            sh_power_state = ov_client.server_hardware.get(uuid)["powerState"]

            if sh_power_state == "On":
                reset_type_dict["PushPowerButton"]["powerState"] = "Off"
            else:
                reset_type_dict["PushPowerButton"]["powerState"] = "On"

        ov_client.server_hardware.update_power_state(new_state, uuid)

        return Response(
            response='{"ResetType": "%s"}' % reset_type,
            status=status.HTTP_200_OK,
            mimetype='application/json')

    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.error(e)
        abort(status.HTTP_404_NOT_FOUND)

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.error('Mapping error: {}'.format(e))
        abort(status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@computer_system.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """Creates a Bad Request Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Invalid information"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@computer_system.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "URL/data not found"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@computer_system.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates an Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype='application/json')
