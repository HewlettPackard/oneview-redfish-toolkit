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

# Python libs
import logging
import time

# 3rd party libs
from flask import abort
from flask import g
from flask import request
from flask_api import status

# own libs
from hpOneView import HPOneViewException

from oneview_redfish_toolkit.api.errors import OneViewRedfishException
from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.config import PERFORMANCE_LOGGER_NAME
from oneview_redfish_toolkit import multiple_oneview


def create_handlers(app):
    @app.before_request
    def init_performance_data():
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            g.start_time_req = time.time()
            g.elapsed_time_ov = 0

    @app.before_request
    def has_odata_version_header():
        """Deny request that specify a different OData-Version than 4.0"""
        odata_version_header = request.headers.get("OData-Version")

        if odata_version_header is None:
            pass
        elif odata_version_header != "4.0":
            abort(status.HTTP_412_PRECONDITION_FAILED,
                  "The request specify a different OData-Version "
                  "header then 4.0. This server also responds "
                  "to requests without the OData-Version header")

    @app.after_request
    def set_odata_version_header(response):
        """Set OData-Version header for all responses"""
        response.headers["OData-Version"] = "4.0"
        return response

    @app.after_request
    def log_performance_data(response):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            end_time = time.time()
            req_time = end_time - g.start_time_req
            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "OneView process: " + str(g.elapsed_time_ov))
            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "Redfish process: " + str(req_time - g.elapsed_time_ov))
            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "Total process: " + str(req_time))
        return response

    @app.errorhandler(status.HTTP_400_BAD_REQUEST)
    def bad_request(error):
        """Creates a Bad Request Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_400(error)

    @app.errorhandler(status.HTTP_401_UNAUTHORIZED)
    def unauthorized_error(error):
        """Creates a Unauthorized Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_401(error)

    @app.errorhandler(status.HTTP_403_FORBIDDEN)
    def forbidden(error):
        """Creates a Forbidden Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_403(error)

    @app.errorhandler(status.HTTP_404_NOT_FOUND)
    def not_found(error):
        """Creates a Not Found Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_404(error)

    @app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server_error(error):
        """Creates an Internal Server Error response"""
        logging.error(error)

        return ResponseBuilder.error_500(error)

    @app.errorhandler(status.HTTP_501_NOT_IMPLEMENTED)
    def not_implemented(error):
        """Creates a Not Implemented Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_501(error)

    @app.errorhandler(HPOneViewException)
    def hp_oneview_client_exception(exception):
        logging.exception(exception)
        response = ResponseBuilder.error_by_hp_oneview_exception(exception)

        # checking if session has expired on Oneview
        if config.auth_mode_is_session() and \
                response.status_code == status.HTTP_401_UNAUTHORIZED:
            token = request.headers.get('x-auth-token')
            client_session.clear_session_by_token(token)

        return response

    @app.errorhandler(OneViewRedfishException)
    def oneview_redfish_exception(exception):
        logging.exception(exception)

        return ResponseBuilder.oneview_redfish_exception(exception)


def initialize_components():
    # Init cached data
    client_session.init_map_clients()
    client_session.init_gc_for_expired_sessions()
    multiple_oneview.init_map_resources()
    multiple_oneview.init_map_appliances()
    category_resource.init_map_category_resources()

    # Init Event Service
    scmb.init_event_service()
