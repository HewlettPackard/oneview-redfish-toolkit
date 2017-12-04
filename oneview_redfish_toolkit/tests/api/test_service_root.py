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

"""
    Tests for redfish_json_validator.py
"""

import unittest
from unittest import mock

from oneview_redfish_toolkit.api.service_root import ServiceRoot
from oneview_redfish_toolkit import util


class TestServiceRoot(unittest.TestCase):
    """Tests for ServiceRoot class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation """

        # Load configuration on util module
        util.load_config('redfish.conf')

    def test_class_instantiation(self):
        """Tests class instantiation and validation"""

        try:
            service_root = ServiceRoot('00000000-0000-0000-0000-000000000000')
        except Exception as e:
            self.fail("Failed to instantiate service root. Error: ".format(e))
        self.assertIsInstance(service_root, ServiceRoot)

    def test_serialize(self):
        """Tests the serialize function result against known result"""

        service_root = ServiceRoot('00000000-0000-0000-0000-000000000000')
        json_str = service_root.serialize()

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ServiceRoot.json'
        ) as f:
            service_root_mockup = f.read()
        self.assertEqual(service_root_mockup, json_str)
