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
from oneview_redfish_toolkit.api.service_root import ServiceRoot
from oneview_redfish_toolkit import util

service_root = Blueprint('service_root', __name__)


@service_root.route('/', methods=["GET"])
def get_service_root():
    """Gets ServiceRoot

        Recover OneView UUID from appliance and creates
        ServiceRoot redfish JSON
    """

    try:
        # Recover OV connection
        oneview_client = util.get_oneview_client()

        # Gets serverhardware for given UUID
        appliance_node_information = \
            oneview_client.appliance_node_information.get_version()
        uuid = appliance_node_information['uuid']

        sr = ServiceRoot(uuid)
        json_str = sr.serialize()
        return Response(
            response=json_str,
            status=200,
            mimetype='application/json')
    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            logging.error("Resource not found: {}".format(e))
            abort(status.HTTP_404_NOT_FOUND)
        else:
            logging.error("OneView Exception: {}".format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logging.error('ServiceRoot error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@service_root.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    return Response(
        response='{"error": "URL/data not found"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@service_root.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates an Internal Server Error response"""
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype='application/json')
