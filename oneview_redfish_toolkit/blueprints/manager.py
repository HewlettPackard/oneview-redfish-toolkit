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
from oneview_redfish_toolkit.api.blade_manager import BladeManager
from oneview_redfish_toolkit.api.enclosure_manager import EnclosureManager
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import util

manager = Blueprint("manager", __name__)


@manager.route("/redfish/v1/Managers/<uuid>", methods=["GET"])
def get_managers(uuid):
    """Get the Redfish Managers.

        Get method to return Managers JSON when
        /redfish/v1/Managers/id is requested.

        Returns:
            JSON: JSON with Managers info for Enclosure or ServerHardware.
    """
    try:
        ov_client = util.get_oneview_client()

        ov_info = ov_client.appliance_node_information.get_version()
        ov_version = ov_info['softwareVersion']

        index_obj = ov_client.index_resources.get_all(filter='uuid=' + uuid)

        if index_obj:
            category = index_obj[0]["category"]
        else:
            raise OneViewRedfishError('Cannot find Index resource')

        if category == 'server-hardware':
            ov_sh = ov_client.server_hardware.get(uuid)
            manager = BladeManager(ov_sh, ov_version)
        elif category == 'enclosures':
            ov_encl = ov_client.enclosures.get(uuid)
            manager = EnclosureManager(ov_encl, ov_version)
        else:
            raise OneViewRedfishError('Enclosure type not found')

        json_str = manager.serialize()
        logging.info(json_str)

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
        abort(status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@manager.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    return Response(
        response='{"error": "URL/data not found"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@manager.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates an Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype='application/json')
