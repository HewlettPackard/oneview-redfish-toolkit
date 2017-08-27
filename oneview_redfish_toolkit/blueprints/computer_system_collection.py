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
from flask import current_app
from flask import jsonify
from flask import make_response
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection

computer_system_collection = Blueprint("computer_system_collection", __name__)


def get_ov_client():
    """Get the Oneview Client

        Returns:
            Object: OneViewClient
    """
    return current_app.oneview_client


@computer_system_collection.route("/", methods=["GET"])
def get_computer_system_collection():
    """Get the Redfish Computer System Collection.

        Get method to return ComputerSystemCollection JSON when
        /redfish/v1/Systems is requested.

        Returns:
                JSON: JSON with ComputerSystemCollection.
    """
    try:
        oneview_server_hardwares = get_ov_client().server_hardware.get_all()
    except OSError:
        return abort(status.HTTP_404_NOT_FOUND)

    computer_system_collection_obj = ComputerSystemCollection(
        current_app.schemas_dict["ComputerSystemCollection"],
        oneview_server_hardwares)

    json_str = computer_system_collection_obj.serialize(True)

    return Response(
        response=json_str,
        status=status.HTTP_200_OK,
        mimetype="application/json")


@computer_system_collection.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found_computer_system_collection(error):
    """Improve not found error message.

        Show a JSON with not found error message
        to Computer system collection.

        Returns:
                JSON: error message.
    """
    return make_response(jsonify(
        {"error": "Computer System Collection not found."}),
        status.HTTP_404_NOT_FOUND)
