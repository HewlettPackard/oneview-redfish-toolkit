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

# 3rd party libs
from flask import Blueprint
from flask import g

# own libs
from oneview_redfish_toolkit.api.chassis_collection import ChassisCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder


chassis_collection = Blueprint("chassis_collection", __name__)


@chassis_collection.route("/redfish/v1/Chassis/", methods=["GET"])
def get_chassis_collection():
    """Get the Redfish Chassis Collection.

        Return ChassisCollection redfish JSON.
        Logs exception of any error and return
        Internal Server Error or Not Found.

        Returns:
            JSON: Redfish json with ChassisCollection.
            When Server hardware, enclosures or racks is not found
            calls abort(404).

        Exceptions:
            OneViewRedfishResourceNotFoundError: if have some oneview resource
            with empty value (ServerHardware, Enclosures or Racks).
            Logs the exception and call abort(404).

            Exception: Generic error, logs the exception and call abort(500).
    """

    # Gets all enclosures
    enclosures = g.oneview_client.enclosures.get_all()

    # Gets all racks
    racks = g.oneview_client.racks.get_all()

    # Gets all server hardware
    server_hardware_list = g.oneview_client.server_hardware.get_all()

    # Build Chassis Collection object and validates it
    cc = ChassisCollection(server_hardware_list, enclosures,
                           racks)

    return ResponseBuilder.success(cc)
