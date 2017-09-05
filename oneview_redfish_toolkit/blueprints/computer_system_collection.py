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

from flask import abort
from flask import Blueprint
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection
from oneview_redfish_toolkit import util

import logging


computer_system_collection = Blueprint("computer_system_collection", __name__)


@computer_system_collection.route("/redfish/v1/Systems/", methods=["GET"])
def get_computer_system_collection():
    """Get the Redfish Computer System Collection.

        Get method to return ComputerSystemCollection JSON when
        /redfish/v1/Systems is requested.

        Returns:
                JSON: JSON with ComputerSystemCollection.
    """
    try:
        # Recover OV connection
        ov_client = util.get_oneview_client()

        # Gets all server hardware
        oneview_server_hardwares = ov_client.server_hardware.get_all()

        # Build Computer System Collection object and validates it
        csc = ComputerSystemCollection(oneview_server_hardwares)

        # Build redfish json
        json_str = csc.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except Exception as e:
        # In case of error print exception and abort
        logging.error(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@computer_system_collection.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates a Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype="application/json")
