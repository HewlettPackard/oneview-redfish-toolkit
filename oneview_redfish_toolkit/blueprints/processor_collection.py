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

# 3rd party libs

from flask import Blueprint
from flask import g

# Own libs
from oneview_redfish_toolkit.api.processor_collection \
    import ProcessorCollection
from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection
from oneview_redfish_toolkit.blueprints.util.response_builder \
    import ResponseBuilder

processor_collection = Blueprint("processor_collection", __name__)


@processor_collection.route(
    ResourceBlockCollection.BASE_URI + "/<uuid>/Systems/1/Processors/",
    methods=["GET"])
def get_processor_collection(uuid):
    """Get the Redfish Resource Block System Processor Collection.

        Get method to return Resource Block System Processor Collection JSON.

        Returns:
            JSON: JSON with Resource Block System Processor Collection info.
    """

    server_hardware = g.oneview_client.server_hardware.get(uuid)

    processor_collection = ProcessorCollection(server_hardware)

    return ResponseBuilder.success(
        processor_collection,
        {"ETag": "W/" + server_hardware["eTag"]})
