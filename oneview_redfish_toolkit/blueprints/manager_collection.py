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
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api.manager_collection import ManagerCollection
from oneview_redfish_toolkit import util

manager_collection = Blueprint("manager_collection", __name__)


@manager_collection.route("/redfish/v1/Managers/", methods=["GET"])
def get_manager_collection():
    """Get the Redfish Manager Collection.

        Return ManagerCollection redfish JSON.
        Logs exception of any error and return
        Internal Server Error or Not Found.

        Returns:
            JSON: Redfish json with ManagerCollection.
            When Server hardwares or enclosures is not found
            calls abort(404).

        Exceptions:
            OneViewRedfishResourceNotFoundError: if have some oneview resource
            with empty value (ServerHardware or Enclosures).
            Logs the exception and call abort(404).

            Exception: Generic error, logs the exception and call abort(500).
    """

    try:
        # Recover OV connection
        ov_client = util.get_oneview_client()

        # Gets all enclosures
        oneview_enclosures = ov_client.enclosures.get_all()

        if not oneview_enclosures:
            raise OneViewRedfishResourceNotFoundError(
                "enclosures", "oneview-result")

        # Gets all server hardware
        oneview_server_hardwares = ov_client.server_hardware.get_all()

        if not oneview_server_hardwares:
            raise OneViewRedfishResourceNotFoundError(
                "server-hardwares", "oneview-result")

        # Build Manager Collection object and validates it
        mc = ManagerCollection(oneview_server_hardwares, oneview_enclosures)

        # Build redfish json
        json_str = mc.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")

    except OneViewRedfishResourceNotFoundError as e:
        # In case of error print exception and abort
        logging.error(e)
        abort(status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # In case of error print exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@manager_collection.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Resource not found"}',
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@manager_collection.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates a Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype="application/json")
