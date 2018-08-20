# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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
from flask_api import status
from werkzeug.exceptions import abort

from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.storage import Storage
from oneview_redfish_toolkit.api.storage_drive_composed_details import \
    StorageDriveComposedDetails
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

storage = Blueprint("storage", __name__)


@storage.route(ComputerSystem.BASE_URI + "/<uuid>/Storage/1", methods=["GET"])
def get_storage(uuid):
    """Get the Redfish Storage for a given UUID.

        Return Storage Redfish JSON for a given server profile UUID.
        Logs exception of any error and return abort(500)
        Internal Server Error.

        Returns:
            JSON: Redfish json with Storage
            When server profile or server hardware type is not found
            calls abort(404)

        Exceptions:
            Logs the exception and call abort(500)

    """
    server_profile = g.oneview_client.server_profiles.get(uuid)
    sht_uri = server_profile['serverHardwareTypeUri']
    server_hardware_type = \
        g.oneview_client.server_hardware_types.get(sht_uri)
    sas_logical_jbods = _find_sas_logical_jbods_by(server_profile)

    st = Storage(server_profile, server_hardware_type, sas_logical_jbods)

    return ResponseBuilder.success(st)


@storage.route(ComputerSystem.BASE_URI +
               "/<profile_id>/Storage/1/Drives/<drive_id>",
               methods=["GET"])
def get_drive(profile_id, drive_id):
    """Get the Redfish Storage for a given UUID.

        Return Drive Redfish JSON for a given server profile UUID and Drive ID.
        Logs exception of any error and return abort(500)
        Internal Server Error.

        Returns:
            JSON: Redfish json with Storage
            When server profile is not found calls abort(404)

        Exceptions:
            Logs the exception and call abort(500)

    """

    drive_id_int = None
    logical_jbod = None
    try:
        drive_id_int = int(drive_id)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, "Drive id should be a integer")

    server_profile = g.oneview_client.server_profiles.get(profile_id)
    sas_logical_jbods = _find_sas_logical_jbods_by(server_profile)

    logical_jbod = _get_logical_jbod(drive_id_int, logical_jbod,
                                     sas_logical_jbods)

    if logical_jbod is None:
        abort(status.HTTP_404_NOT_FOUND, "Drive {} not found"
              .format(drive_id))

    drive_details = StorageDriveComposedDetails(drive_id_int,
                                                server_profile,
                                                logical_jbod)

    return ResponseBuilder.success(drive_details)


def _get_logical_jbod(drive_id_int, logical_jbod, sas_logical_jbods):
    logical_jbods_sorted = sorted(sas_logical_jbods, key=lambda i: i["uri"])

    count_drives = 0
    for log_jbod in logical_jbods_sorted:
        next_count = count_drives + int(log_jbod["numPhysicalDrives"])

        if drive_id_int in range(count_drives + 1, next_count + 1):
            logical_jbod = log_jbod
            break

        count_drives = next_count

    return logical_jbod


def _find_sas_logical_jbods_by(server_profile):
    sas_logical_jbods = []
    for logical_jbod in server_profile["localStorage"]["sasLogicalJBODs"]:
        if logical_jbod["sasLogicalJBODUri"]:
            item = g.oneview_client.sas_logical_jbods\
                .get(logical_jbod["sasLogicalJBODUri"])
            sas_logical_jbods.append(item)

    return sas_logical_jbods
