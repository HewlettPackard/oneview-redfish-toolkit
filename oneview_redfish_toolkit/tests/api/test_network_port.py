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

import json

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
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

        try:
            network_port = \
                NetworkPort(
                    self.device_id,
                    self.port_id,
                    self.server_hardware)
        except Exception as e:
            self.fail("Failed to instantiate NetworkPort class."
                      " Error: {}".format(e))
        self.assertIsInstance(
            network_port,
            NetworkPort)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            network_port = \
                NetworkPort(
                    self.device_id,
                    self.port_id,
                    self.server_hardware)
        except Exception as e:
            self.fail("Failed to instantiate NetworkPort class."
                      " Error: {}".format(e))

        try:
            result = json.loads(network_port.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqualMockup(self.network_port_mockup, result)

    def test_invalid_port_id(self):
        # Tests if class with an invalid port_id

        try:
            network_port = NetworkPort(
                self.device_id,
                "invalid_port_id",
                self.server_hardware)
        except OneViewRedfishError as e:
            self.assertIsInstance(e, OneViewRedfishError)
        except Exception as e:
            self.fail("Failed to instantiate NetworkPort class."
                      " Error: {}".format(e))
        else:
            self.fail("Class instantiated with invalid parameters."
                      " Error: {}".format(network_port))
