# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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
from flask_api import status
from werkzeug.exceptions import abort

from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api.storage_composition_details import \
    StorageCompositionDetails
from oneview_redfish_toolkit.api.storage_drive_composition_details import \
    StorageDriveCompositionDetails
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

storage_composition_details = Blueprint("storage_composition_details",
                                        __name__)

FROZEN_ID = "1"


@storage_composition_details.route(
    ResourceBlock.BASE_URI +
    "/<resource_block_uuid>/Storage/<storage_id>", methods=["GET"])
def get_storage_details(resource_block_uuid, storage_id):
    """Get the Redfish Storage details of a Storage ResourceBlock for a given ID.

        Return Storage redfish JSON for a given ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with Storage detail information.
    """

    if str(storage_id) != FROZEN_ID:
        abort(status.HTTP_404_NOT_FOUND,
              "Storage {} not found for ResourceBlock {}"
              .format(storage_id, resource_block_uuid))

    drive = g.oneview_client.index_resources.get(
        '/rest/drives/' + resource_block_uuid)
    result = StorageCompositionDetails(drive)

    return ResponseBuilder.success(result)


@storage_composition_details.route(
    ResourceBlock.BASE_URI +
    "/<resource_block_uuid>/Storage/<storage_id>/Drives/<drive_id>",
    methods=["GET"])
def get_storage_drive_details(resource_block_uuid, storage_id, drive_id):
    """Get the Redfish Drive details of a Storage of a Storage Resource Block

        Return Drive redfish JSON for a given ID.
        Logs exception of any error and return Internal Server
        Error or Not Found.

        Returns:
            JSON: Redfish json with Drive detail information.
    """

    drive = g.oneview_client.index_resources.get(
        '/rest/drives/' + resource_block_uuid)

    if str(storage_id) != FROZEN_ID:
        abort(status.HTTP_404_NOT_FOUND,
              "Storage {} not found for ResourceBlock {}"
              .format(storage_id, resource_block_uuid))

    if str(drive_id) != FROZEN_ID:
        abort(status.HTTP_404_NOT_FOUND,
              "Drive {} not found for Storage {} of ResourceBlock {}"
              .format(drive_id, storage_id, resource_block_uuid))

    drive_encl_uri = drive["attributes"]["driveEnclosureUri"].split('/')[-1]
    drive_enclosure = g.oneview_client.drive_enclosures.get(drive_encl_uri)
    result = StorageDriveCompositionDetails(drive, drive_enclosure)

    return ResponseBuilder.success(result)
