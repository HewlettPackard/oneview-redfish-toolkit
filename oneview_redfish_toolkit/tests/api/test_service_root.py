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

"""
    Tests for redfish_json_validator.py
"""

import json
from unittest import mock

from oneview_redfish_toolkit.api.service_root import ServiceRoot
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestServiceRoot(BaseTest):
    """Tests for ServiceRoot class"""

    def test_class_instantiation(self):
        """Tests class instantiation and validation"""

        try:
            service_root = ServiceRoot('00000000-0000-0000-0000-000000000000')
        except Exception as e:
            self.fail("Failed to instantiate service root. "
                      "Error: {}".format(e))
        self.assertIsInstance(service_root, ServiceRoot)

    @mock.patch.object(config, 'get_authentication_mode')
    def test_serialize(self, config_mock):
        """Tests the serialize function result against known result"""

        config_mock.return_value = "conf"

        service_root = ServiceRoot('00000000-0000-0000-0000-000000000000')
        result = json.loads(service_root.serialize())

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ServiceRoot.json'
        ) as f:
            service_root_mockup = json.load(f)
        self.assertEqualMockup(service_root_mockup, result)
