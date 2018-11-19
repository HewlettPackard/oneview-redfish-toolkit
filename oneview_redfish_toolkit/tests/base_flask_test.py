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
from unittest import mock

from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit import handler_multiple_oneview
from oneview_redfish_toolkit import initialize_app
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

        cls.patcher_get_client_by_token = mock.patch(
            'oneview_redfish_toolkit.client_session.'
            '_get_oneview_client_by_token')
        cls.mock_get_client_by_token = cls.patcher_get_client_by_token.start()

        cls.patcher_get_client_by_ip = mock.patch(
            'oneview_redfish_toolkit.client_session.'
            '_get_oneview_client_by_ip')
        cls.mock_get_client_by_ip = cls.patcher_get_client_by_ip.start()

        multiple_oneview.init_map_resources()

        # same configuration applied to Flask in app.py
        cls.app.url_map.strict_slashes = False

        initialize_app.create_handlers(cls.app)

        @cls.app.before_request
        def check_authentication():
            # Cached OneView's connections for the same request
            g.ov_connections = dict()

            g.elapsed_time_ov = 0

            g.oneview_client = \
                handler_multiple_oneview.MultipleOneViewResource()

        cls.client = cls.app.test_client()

        # propagate the exceptions to the test client
        cls.app.testing = False

    @classmethod
    def setUp(cls):
        cls.oneview_client = mock.MagicMock()
        cls.mock_get_client_by_ip.return_value = cls.oneview_client
        cls.mock_get_client_by_token.return_value = cls.oneview_client
        category_resource.init_map_category_resources()

    @classmethod
    def tearDownClass(cls):
        cls.patcher_get_client_by_ip.stop()
        cls.patcher_get_client_by_token.stop()
