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

from oneview_redfish_toolkit.api.service_root import ServiceRoot
from oneview_redfish_toolkit import util
import unittest


class TestServiceRoot(unittest.TestCase):

    def test_class_instantiation(self):
        # Tests if class is correctly instanciated
        obj = ServiceRoot('schema')
        self.assertIsInstance(obj, ServiceRoot)

    def test_validation(self):
        # Tests if expected filed exists and are correctly populated by
        # the constructor

        cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')
        schemas = dict(cfg.items('schemas'))
        schemas_dict = util.load_schemas('oneview_redfish_toolkit/schemas',
                                         schemas)
        obj = ServiceRoot(schemas_dict['ServiceRoot'])
        self.assertTrue(obj._Validate())

    def teste_serialize(self):
        # Tests the serialize function result against known result

        cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')
        schemas = dict(cfg.items('schemas'))
        schemas_dict = util.load_schemas('oneview_redfish_toolkit/schemas',
                                         schemas)
        obj = ServiceRoot(schemas_dict['ServiceRoot'])
        json_str = obj.Serialize(True)

        with open(
            'oneview_redfish_toolkit/tests/mockups/ServiceRoot.mok'
        ) as F:
            mok_json = F.read()
        self.assertEqual(json_str, mok_json)


if __name__ == '__main__':
    unittest.main()
