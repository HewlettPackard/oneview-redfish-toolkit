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
from flask import abort
from flask import Blueprint
from flask import g
from flask_api import status

# Own libs
from oneview_redfish_toolkit.api.processor import Processor
from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection
from oneview_redfish_toolkit.blueprints.util.response_builder \
    import ResponseBuilder

processor = Blueprint("processor", __name__)


@processor.route(
    ResourceBlockCollection.BASE_URI + "/<uuid>/Systems/1/Processors/<id>",
    methods=["GET"])
def get_processor(uuid, id):
    """Get the Redfish Resource Block System Processor.

        Get method to return Resource Block System Processor JSON.

        Returns:
            JSON: JSON with Resource Block System Processor info.
    """

    try:
        processor_id = int(id)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST,
              "Cannot convert processor_id {} to integer".format(id))

    server_hardware = g.oneview_client.server_hardware.get_by_id(uuid).data
    processor_count = server_hardware["processorCount"]

    if processor_id < 1 or processor_id > processor_count:
        abort(status.HTTP_404_NOT_FOUND,
              "Invalid processor identifier {}".format(processor_id))

    processor = Processor(server_hardware, str(processor_id))

    return ResponseBuilder.success(
        processor, {"ETag": "W/" + server_hardware["eTag"]})
