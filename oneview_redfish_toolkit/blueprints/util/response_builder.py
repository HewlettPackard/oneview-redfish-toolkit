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

from collections import namedtuple

from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.errors import AUTH_ONEVIEW_ERRORS
from oneview_redfish_toolkit.api.errors import NOT_FOUND_ONEVIEW_ERRORS
from oneview_redfish_toolkit.api.redfish_error import RedfishError


ErrorDescription = namedtuple('ErrorDescription', ['description'])


class ResponseBuilder(object):

    @staticmethod
    def response(serializable_data, http_status, headers={}):
        return Response(
            response=serializable_data.serialize(),
            status=http_status,
            mimetype="application/json",
            headers=headers)

    @staticmethod
    def success(api_data, headers={}):
        return ResponseBuilder.response(api_data, status.HTTP_200_OK, headers)

    @staticmethod
    def error_by_hp_oneview_exception(exception):
        error_code = exception.oneview_response['errorCode']
        http_error_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if error_code in NOT_FOUND_ONEVIEW_ERRORS:
            http_error_code = status.HTTP_404_NOT_FOUND
        elif error_code in AUTH_ONEVIEW_ERRORS:
            http_error_code = status.HTTP_401_UNAUTHORIZED

        method_name = 'error_' + str(http_error_code)
        handler_method_to_call = getattr(ResponseBuilder, method_name)

        error_desc = ErrorDescription(description=exception.msg)
        return handler_method_to_call(error_desc)

    @staticmethod
    def error_401(error):
        redfish_error = RedfishError("GeneralError", error.description)
        return ResponseBuilder.response(redfish_error,
                                        status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def error_403(error):
        redfish_error = RedfishError("GeneralError", error.description)
        return ResponseBuilder.response(redfish_error,
                                        status.HTTP_403_FORBIDDEN)

    @staticmethod
    def error_404(error):
        redfish_error = RedfishError("GeneralError", error.description)
        return ResponseBuilder.response(redfish_error,
                                        status.HTTP_404_NOT_FOUND)

    @staticmethod
    def error_500(error):
        if hasattr(error, "description"):
            msg = error.description
        else:
            msg = str(error)

        redfish_error = RedfishError("InternalError", msg)
        redfish_error.add_extended_info("InternalError")
        return ResponseBuilder.response(redfish_error,
                                        status.HTTP_500_INTERNAL_SERVER_ERROR)
