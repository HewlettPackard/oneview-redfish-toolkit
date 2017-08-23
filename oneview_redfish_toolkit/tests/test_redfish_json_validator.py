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
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
import unittest


class TestRedfishJsonValidator(unittest.TestCase):

    def test(self):
        # Tests if class is correctly instanciated
        obj = RedfishJsonValidator('schema')
        self.assertIsInstance(obj, RedfishJsonValidator)

    def test_has_valid_config_file(self):
        # Tests if expected filed exists and are correctly populated by
        # the constructor

        obj = RedfishJsonValidator('schema')
        self.assertEqual(obj.schema_obj, 'schema')
        self.assertIsInstance(obj.redfish, collections.OrderedDict)


if __name__ == '__main__':
    unittest.main()
