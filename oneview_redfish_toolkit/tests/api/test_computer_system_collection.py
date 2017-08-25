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
    Tests for computer_system_collection.py
"""

import json

from oneview_redfish_toolkit.api.computer_system_collection \
    import ComputerSystemCollection
from oneview_redfish_toolkit import util

import unittest


class TestComputerSystemCollection(unittest.TestCase):

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated
        obj = ComputerSystemCollection('schema', {})
        self.assertIsInstance(obj, ComputerSystemCollection)

    def test_validation(self):
        # Tests if expected filed exists and are correctly populated by
        # the constructor
        cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')
        schemas = dict(cfg.items('schemas'))
        schemas_dict = util.load_schemas('oneview_redfish_toolkit/schemas',
                                         schemas)

        with open(
            'oneview_redfish_toolkit/tests/mockups/'
            'ServerHardwares.json'
        ) as f:
            mok_json = f.read()

        obj = ComputerSystemCollection(
            schemas_dict['ComputerSystemCollection'], json.loads(mok_json))
        self.assertTrue(obj._validate())

    def test_serialize(self):
        # Tests the serialize function result against known result
        cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')
        schemas = dict(cfg.items('schemas'))
        schemas_dict = util.load_schemas('oneview_redfish_toolkit/schemas',
                                         schemas)

        with open(
            'oneview_redfish_toolkit/tests/mockups/'
            'ServerHardwares.json'
        ) as f:
            mok_json = f.read()

        obj = ComputerSystemCollection(
            schemas_dict['ComputerSystemCollection'], json.loads(mok_json))
        json_str = obj.serialize(pretty=True)

        with open(
            'oneview_redfish_toolkit/tests/mockups/'
            'ComputerSystemCollection.json'
        ) as f:
            mok_json_result = f.read()

        self.assertEqual(json_str, mok_json_result)
