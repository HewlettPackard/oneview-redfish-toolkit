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

import collections
import unittest
from unittest import mock

from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit import util


class TestRedfishJsonValidator(unittest.TestCase):

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneviwe_client_mockup):
        """Tests preparation """

        # Load configuration on util module
        util.load_config('redfish.conf')

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated
        try:
            redfish_json_validator = RedfishJsonValidator('ServiceRoot')
        except Exception as e:
            self.fail("Failed to instantiate RedfishJsonValidator class."
                      " Error: {}".format(e))
        self.assertIsInstance(redfish_json_validator, RedfishJsonValidator)

    def test_has_valid_config_file(self):
        # Tests if expected filed exists and are correctly populated by
        # the constructor

        redfish_json_validator = RedfishJsonValidator('ServiceRoot')
        self.assertIsInstance(redfish_json_validator.schema_obj, dict)
        self.assertIsInstance(
            redfish_json_validator.redfish,
            collections.OrderedDict
        )
