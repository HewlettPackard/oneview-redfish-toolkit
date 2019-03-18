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


from copy import deepcopy
import json

from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishInvalidAttributeValueException
from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishResourceNotFoundException
from oneview_redfish_toolkit.api.network_device_function import \
    NetworkDeviceFunction
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestNetworkDeviceFunction(BaseTest):
    """Tests for NetworkDeviceFunction class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerHardware mockup
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading NetworkDeviceFunction mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkDeviceFunction1_1_a.json'
        ) as f:
            self.network_device_function_mockup = json.load(f)

        self.device_id = "3"
        self.device_function_id = "1_1_a"

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        network_device_function = \
            NetworkDeviceFunction(
                self.device_id,
                self.device_function_id,
                self.server_hardware)
        self.assertIsInstance(
            network_device_function,
            NetworkDeviceFunction)

    def test_serialize(self):
        # Tests the serialize function result against known result

        network_device_function = \
            NetworkDeviceFunction(
                self.device_id,
                self.device_function_id,
                self.server_hardware)

        result = json.loads(network_device_function.serialize())

        self.assertEqualMockup(self.network_device_function_mockup, result)

    def test_invalid_device_function_id(self):
        # Tests if class with an invalid device_function_id

        try:
            network_device_function = NetworkDeviceFunction(
                self.device_id,
                "invalid_device_id",
                self.server_hardware)
        except OneViewRedfishResourceNotFoundException as e:
            self.assertIsInstance(e,
                                  OneViewRedfishResourceNotFoundException)
        except Exception as e:
            self.fail("Failed to instantiate NetworkDeviceFunction class."
                      " Error: {}".format(e))
        else:
            self.fail("Class instantiated with invalid parameters."
                      " Error: {}".format(network_device_function))

    def test_port_type_fibre_channel_exception(self):
        # Tests if class with an invalid device_function_id

        try:
            server_hardware = deepcopy(self.server_hardware)
            server_hardware["portMap"]["deviceSlots"][2]["physicalPorts"][0]["type"]\
                = "FibreChannel"
            NetworkDeviceFunction(self.device_id, self.device_function_id,
                                  server_hardware)
        except OneViewRedfishInvalidAttributeValueException as e:
            self.assertIsInstance(e,
                                  OneViewRedfishInvalidAttributeValueException)
            self.assertEqual(e.msg, "FibreChannel not implemented")

    def test_invalid_port_exception(self):
        # Tests if class with an invalid device_function_id

        try:
            server_hardware = deepcopy(self.server_hardware)
            server_hardware["portMap"]["deviceSlots"][2]["physicalPorts"][0]["type"]\
                = "InvalidPort"
            NetworkDeviceFunction(self.device_id, self.device_function_id,
                                  server_hardware)
        except OneViewRedfishInvalidAttributeValueException as e:
            self.assertIsInstance(e,
                                  OneViewRedfishInvalidAttributeValueException)
            self.assertEqual(e.msg, "Type not supported")
