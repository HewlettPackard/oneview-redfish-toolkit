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
    Tests for load_schemas function from util.py
"""

import collections
from oneview_redfish_toolkit import util
import unittest


class TestUtilLoadConfig(unittest.TestCase):

    def setUp(self):
        self.schema_dir = './oneview_redfish_toolkit/schemas'
        self.config_file = './oneview_redfish_toolkit/redfish.ini'

    def test_invalid_schema_dir(self):
        # Tests if passing a non existing schema dir returns False

        schemas = dict()
        self.assertFalse(util.load_schemas('non-exist-schema-dir', schemas))

    def test_valid_schema_dir_invalid_dict(self):
        # Tests if passing a valid schemadir and an invalid schema dict
        # returns False

        schemas = dict()
        schemas['failed'] = 'fail.json'
        self.assertFalse(util.load_schemas(self.schema_dir, schemas))

    def test_valid_schema_dir_valid_dict(self):
        # Tests if ini file has all expected sections

        cfg = util.load_config(self.config_file)

        schemas = dict(cfg.items('schemas'))
        schemas_dict = util.load_schemas(self.schema_dir, schemas)

        self.assertIsInstance(schemas_dict, collections.OrderedDict,
                              msg='Loading schemas didnt return a dict')
