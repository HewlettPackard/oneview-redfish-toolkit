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

import collections
import json
from unittest import mock

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit.tests.base_test import BaseTest

service_root_version = 'v1_2_0'
zone_version = 'v1_1_0'

schemas_dict = collections.OrderedDict()
schemas_dict['ServiceRoot'] = 'ServiceRoot.' + service_root_version + '.json'
schemas_dict['Zone'] = 'Zone.' + zone_version + '.json'


class TestRedfishJsonValidator(BaseTest):

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
        self.assertIsInstance(
            redfish_json_validator.redfish,
            collections.OrderedDict)

    def test_get_resource_by_id(self):
        redfish_json_validator = RedfishJsonValidator('ServiceRoot')

        # Loading server_hardware mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        device_slot = redfish_json_validator.get_resource_by_id(
            server_hardware["portMap"]["deviceSlots"], "deviceNumber", 3)

        json_device_slot = None

        for i in server_hardware["portMap"]["deviceSlots"]:
            if i["deviceNumber"] == 3:
                json_device_slot = i

        self.assertEqual(device_slot, json_device_slot)

    def test_get_resource_empty_list(self):
        redfish_json_validator = RedfishJsonValidator('ServiceRoot')

        with self.assertRaises(OneViewRedfishResourceNotFoundError):
            redfish_json_validator.get_resource_by_id([], "deviceNumber", 1)

    def test_get_resource_invalid_id(self):
        redfish_json_validator = RedfishJsonValidator('ServiceRoot')

        with self.assertRaises(OneViewRedfishError):
            redfish_json_validator.get_resource_by_id(
                [], "deviceNumber", "INVALID_ID")

    @mock.patch('oneview_redfish_toolkit.api.schemas.SCHEMAS', schemas_dict)
    def test_get_odata_type_by_class(self):
        redfish_json_validator = RedfishJsonValidator('ServiceRoot')
        odata_type_schema_class = '#ServiceRoot.' + \
            service_root_version + '.ServiceRoot'

        zone_schema_name = 'Zone'
        odata_type_zone_schema = '#Zone.' + zone_version + '.Zone'

        self.assertEqual(redfish_json_validator.get_odata_type(),
                         odata_type_schema_class)
        self.assertEqual(
            redfish_json_validator.get_odata_type_by_schema(zone_schema_name),
            odata_type_zone_schema)
