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

# Python libs
import logging

# 3rd party libs
from flask import abort
from flask import Blueprint
from flask import g
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.processor import Processor


processor = Blueprint("processor", __name__)


@processor.route(
    "/redfish/v1/CompositionService/ResourceBlocks/<uuid>/Processors/<id>",
    methods=["GET"])
def get_memory(uuid, id):
    """Get the Redfish Resource Block Processor.

        Get method to return Resource Block Processor JSON when
        /redfish/v1/CompositionService/ResourceBlocks/<uuid>/Processors/<id>
        is requested.

        Returns:
            JSON: JSON with Resource Block Processor info.
    """

    try:
        try:
            processor_id = int(id)
        except Exception as e:
            raise OneViewRedfishError("Invalid processor identifier")

        server_hardware = g.oneview_client.server_hardware.get(uuid)
        processor_count = server_hardware["processorCount"]

        if processor_id < 1 or processor_id > processor_count:
            raise OneViewRedfishError("Invalid processor identifier")

        eTag = server_hardware["eTag"]

        processor = Processor(uuid, id, server_hardware)

        json_str = processor.serialize()

        response = Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
        response.headers.add("ETag", "W/" + eTag)

        return response
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)
        abort(status.HTTP_404_NOT_FOUND, "Processor not found")

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)

    except Exception as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
