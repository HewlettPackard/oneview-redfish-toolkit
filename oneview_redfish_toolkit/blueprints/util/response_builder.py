from collections import namedtuple

from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.redfish_error import RedfishError

HP_ONEVIEW_ERROR_CODE_MAP = {
    'RESOURCE_NOT_FOUND': status.HTTP_404_NOT_FOUND
}

ErrorDescription = namedtuple('ErrorDescription', ['description'])


class ResponseBuilder:

    @staticmethod
    def response(serializable_data, http_status):
        return Response(
            response=serializable_data.serialize(),
            status=http_status,
            mimetype="application/json")

    @staticmethod
    def success(api_data):
        return ResponseBuilder.response(api_data, status.HTTP_200_OK)

    @staticmethod
    def error_by_hp_oneview_exception(exception):
        error_code = exception.oneview_response['errorCode']
        http_error_code = HP_ONEVIEW_ERROR_CODE_MAP.get(error_code)\
            or status.HTTP_500_INTERNAL_SERVER_ERROR

        method_name = 'error_' + str(http_error_code)
        handler_method_to_call = getattr(ResponseBuilder, method_name)

        error_desc = ErrorDescription(description=exception.msg)
        return handler_method_to_call(error_desc)

    @staticmethod
    def error_404(error):
        redfish_error = RedfishError("GeneralError", error.description)
        return ResponseBuilder.response(redfish_error,
                                        status.HTTP_404_NOT_FOUND)

    @staticmethod
    def error_500(error):
        redfish_error = RedfishError(
            "InternalError",
            "The request failed due to an internal service error.  "
            "The service is still operational.")
        redfish_error.add_extended_info("InternalError")
        return ResponseBuilder.response(redfish_error,
                                        status.HTTP_500_INTERNAL_SERVER_ERROR)
