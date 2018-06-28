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
from flask import g
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError

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
        # Gets all server hardware
        server_hardware_list = g.oneview_client.server_hardware.get_all()
        if not server_hardware_list:
            raise OneViewRedfishResourceNotFoundError(
                "server-hardware-list", "Resource")

        # Filter server profiles that has a profile applied
        server_profiles_applied_list = list()
        for server_hardware_item, index in \
                zip(server_hardware_list, range(len(server_hardware_list))):
            if server_hardware_item["state"] == "ProfileApplied":
                server_profiles_applied_list.append(server_hardware_item)

        # Build Computer System Collection object and validates it
        csc = ComputerSystemCollection(server_profiles_applied_list)

        # Build redfish json
        json_str = csc.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except OneViewRedfishResourceNotFoundError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)
    except Exception as e:
        # In case of error print exception and abort
        logging.exception(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
