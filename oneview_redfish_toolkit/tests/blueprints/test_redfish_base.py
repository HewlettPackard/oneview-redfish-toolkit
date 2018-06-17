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

from flask_api import status

from oneview_redfish_toolkit.blueprints.redfish_base import redfish_base
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestRedfishBase(BaseFlaskTest):

    @classmethod
    def setUpClass(self):
        super(TestRedfishBase, self).setUpClass()

        self.app.register_blueprint(redfish_base, url_prefix='/redfish/')

    def test_get_redfish_base_status(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.client.get("/redfish/")

        # assert the status code of the response
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_get_redfish_base_response(self):
        result = self.client.get("/redfish/")

        json_str = result.data.decode("utf-8")

        self.assertEqual(json_str, '{"v1": "/redfish/v1/"}')
