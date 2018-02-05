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

import logging


from flask import abort
from flask import Blueprint
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.event_service \
    import EventService
from oneview_redfish_toolkit import util


event_service = Blueprint("event_service", __name__)


@event_service.route("/redfish/v1/EventService/", methods=["GET"])
def get_event_service():
    """Get the Redfish Event Service.

        Get method to return EventService JSON when
        /redfish/v1/EventService is requested.

        Returns:
            JSON: JSON with EventService.

        Exceptions:
            OneViewRedfishError: General error.
    """
    try:
        # Build Event Service object and validates it
        evs = EventService(util.delivery_retry_attempts,
                           util.delivery_retry_interval)

        # Build redfish json
        json_str = evs.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except OneViewRedfishError as e:
        # In case of error print exception and abort
        logging.exception(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
