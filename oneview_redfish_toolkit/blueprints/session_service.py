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

import logging

from flask import abort
from flask import Blueprint
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.session_service import SessionService

session_service = Blueprint("session_service", __name__)


@session_service.route(SessionService.BASE_URI, methods=["GET"])
def get_session_service():
    """Get the Redfish Session Service.

        Get method to return SessionService JSON when
        /redfish/v1/SessionService is requested.

        Returns:
            JSON: JSON with SessionService.

        Exceptions:
            OneViewRedfishError: General error.
    """
    try:
        # Build Session Service object and validates it
        sessionservice = SessionService()

        # Build redfish json
        json_str = sessionservice.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except OneViewRedfishError as e:
        # In case of error print exception and abort
        logging.exception(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
