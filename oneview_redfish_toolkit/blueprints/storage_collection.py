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

from flask import Blueprint
from flask import g

from oneview_redfish_toolkit.api.storage_collection \
    import StorageCollection


from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

storage_collection = Blueprint("storage_collection", __name__)


@storage_collection.route(
    "/redfish/v1/Systems/<uuid>/Storage", methods=["GET"])
def get_storage_collection(uuid):
    """Get the Redfish Storage Collection.

    Return StorageCollection Redfish JSON.
    """
    # It just verifies if server profile there is in Oneview
    g.oneview_client.server_profiles.get(uuid)

    storage = StorageCollection(uuid)

    return ResponseBuilder.success(storage)
