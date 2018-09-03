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

from flask import Flask
from flask import g
from flask import Response
from flask_api import status
from unittest import mock

from hpOneView import HPOneViewException

from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import handler_multiple_oneview
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit.tests.base_test import BaseTest


class BaseFlaskTest(BaseTest):
    """Base class for tests that need a Flask instance"""

    @classmethod
    def setUpClass(cls):
        super(BaseFlaskTest, cls).setUpClass()

        # creates a test client
        cls.app = Flask(cls.__name__)

        cls.oneview_client = mock.MagicMock()

        cls.patcher_get_oneview_client = mock.patch(
            'oneview_redfish_toolkit.client_session._get_oneview_client_by_token')
        cls.mock_get_oneview_token = cls.patcher_get_oneview_client.start()
        cls.mock_get_oneview_token.return_value = cls.oneview_client

        multiple_oneview.init_map_resources()

        # same configuration applied to Flask in app.py
        cls.app.url_map.strict_slashes = False

        @cls.app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        def internal_server_error(error):
            """General InternalServerError handler for the app"""

            redfish_error = RedfishError(
                "InternalError",
                "The request failed due to an internal service error.  "
                "The service is still operational.")
            redfish_error.add_extended_info("InternalError")
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype="application/json")

        @cls.app.errorhandler(status.HTTP_403_FORBIDDEN)
        def forbidden(error):
            return ResponseBuilder.error_403(error)

        @cls.app.errorhandler(status.HTTP_404_NOT_FOUND)
        def not_found(error):
            """Creates a Not Found Error response"""
            redfish_error = RedfishError(
                "GeneralError", error.description)
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_404_NOT_FOUND,
                mimetype='application/json')

        @cls.app.errorhandler(status.HTTP_400_BAD_REQUEST)
        def bad_request(error):
            """Creates a Bad Request Error response"""
            redfish_error = RedfishError(
                "PropertyValueNotInList", error.description)

            redfish_error.add_extended_info(
                message_id="PropertyValueNotInList",
                message_args=["VALUE", "PROPERTY"],
                related_properties=["PROPERTY"])

            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_400_BAD_REQUEST,
                mimetype='application/json')

        @cls.app.errorhandler(HPOneViewException)
        def hp_oneview_client_exception(exception):
            return ResponseBuilder.error_by_hp_oneview_exception(exception)

        @cls.app.before_request
        def check_authentication():
            # Cached OneView's connections for the same request
            g.ov_connections = dict()

            g.oneview_client = \
                handler_multiple_oneview.MultipleOneViewResource()

        cls.client = cls.app.test_client()

        # propagate the exceptions to the test client
        cls.app.testing = False

    @classmethod
    def setUp(cls):
        cls.oneview_client = mock.MagicMock()
        cls.mock_get_oneview_token.return_value = cls.oneview_client

    @classmethod
    def tearDownClass(cls):
        cls.patcher_get_oneview_client.stop()
