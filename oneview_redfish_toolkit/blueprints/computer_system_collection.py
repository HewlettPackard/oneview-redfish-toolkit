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

from flask import Blueprint
from flask import g

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder


computer_system_collection = Blueprint("computer_system_collection", __name__)


@computer_system_collection.route("/redfish/v1/Systems/", methods=["GET"])
def get_computer_system_collection():
    """Get the Redfish Computer System Collection.

        Get method to return ComputerSystemCollection JSON when
        /redfish/v1/Systems is requested.

        Returns:
                JSON: JSON with ComputerSystemCollection.
    """
    # Gets all server hardware
    server_hardware_list = g.oneview_client.server_hardware.get_all()

    # Filter servers that have a profile applied
    servers_profiled_list = list()
    for server_hardware_item in server_hardware_list:
        if server_hardware_item["state"] == "ProfileApplied":
            servers_profiled_list.append(server_hardware_item)

    # Build Computer System Collection object and validates it
    csc = ComputerSystemCollection(servers_profiled_list)

    # Build response and returns it
    return ResponseBuilder.success(csc)
