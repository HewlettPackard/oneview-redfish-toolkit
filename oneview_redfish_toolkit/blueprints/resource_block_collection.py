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

from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

resource_block_collection = Blueprint("resource_block_collection", __name__)


@resource_block_collection.route(
    "/redfish/v1/CompositionService/ResourceBlocks/", methods=["GET"])
def get_resource_block_collection():
    """Get the Redfish ResourceBlock Collection.

        Return ResourceBlockCollection redfish JSON.
        Logs exception of any error and return
        Internal Server Error or Not Found.

        Returns:
            JSON: Redfish json with ResourceBlockCollection.
    """

    # Gets all server hardware
    server_hardware_list = g.oneview_client.server_hardware.get_all()
    server_profile_template_list = g.oneview_client.\
        server_profile_templates.get_all()
    drives_list = g.oneview_client.index_resources \
        .get_all(category="drives", count=10000)

    # Build ResourceBlockCollection object and validates it
    cc = ResourceBlockCollection(server_hardware_list,
                                 server_profile_template_list,
                                 drives_list)

    return ResponseBuilder.success(cc)
