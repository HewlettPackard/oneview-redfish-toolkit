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
from oneview_redfish_toolkit.api.network_port import \
    NetworkPort
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestNetworkPort(BaseTest):
    """Tests for NetworkPort class"""

    def setUp(self):
        """Tests preparation"""

        # Loading ServerHardware mockup
        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

        # Loading NetworkPort mockup result
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'NetworkPort1-Ethernet.json'
        ) as f:
            self.network_port_mockup = json.load(f)

        self.device_id = "3"
        self.port_id = "1"

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        network_port = \
            NetworkPort(
                self.device_id,
                self.port_id,
                self.server_hardware)
        self.assertIsInstance(
            network_port,
            NetworkPort)

    def test_serialize(self):
        # Tests the serialize function result against known result

        network_port = \
            NetworkPort(
                self.device_id,
                self.port_id,
                self.server_hardware)

        result = json.loads(network_port.serialize())

        self.assertEqualMockup(self.network_port_mockup, result)

    def test_invalid_port_id(self):
        # Tests if class with an invalid port_id

        try:
            NetworkPort(self.device_id, "invalid_port_id",
                        self.server_hardware)
        except OneViewRedfishInvalidAttributeValueException as e:
            self.assertEqual(e.msg, "Invalid NetworkPort ID")

    def test_fibre_channel_type(self):
        # Tests the fibre channel port type

        # Loading server_hardware_fibre_channel mockup value
        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareFibreChannel.json'
        ) as f:
            server_hardware_fibre_channel = json.load(f)

        # Loading NetworkPort mockup result
        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'NetworkPort1-FibreChannel.json'
        ) as f:
            network_port_fb_mockup = json.load(f)

        network_port = \
            NetworkPort(
                "2",
                self.port_id,
                server_hardware_fibre_channel)

        result = json.loads(network_port.serialize())

        self.assertEqualMockup(network_port_fb_mockup, result)

    def test_invalid_port_type_exception(self):
        # Tests an invalid port type exception

        server_hardware = deepcopy(self.server_hardware)
        server_hardware["portMap"]["deviceSlots"][2]["physicalPorts"][0]["type"] \
            = "InvalidPort"

        try:
            NetworkPort(self.device_id, self.port_id,
                        server_hardware)
        except OneViewRedfishInvalidAttributeValueException as e:
            self.assertEqual(e.msg, "Type not supported")
