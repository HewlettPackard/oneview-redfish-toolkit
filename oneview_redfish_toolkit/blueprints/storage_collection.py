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
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.storage_collection \
    import StorageCollection

import logging

storage_collection = Blueprint("storage_collection", __name__)


@storage_collection.route(
    "/redfish/v1/Systems/<uuid>/Storage", methods=["GET"])
def get_storage_collection(uuid):
    """Get the Redfish Storage Collection.

    Return StorageCollection Redfish JSON.
    """

    storage = StorageCollection(uuid)

    json_str = storage.serialize()

    return Response(
        response=json_str,
        status=status.HTTP_200_OK,
        mimetype="application/json")


@storage_collection.errorhandler(
    status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates a Internal Server Error response"""
    logging.error(vars(error))
    return Response(
        response='{"error": "Internal Server Error"}',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype="application/json")
