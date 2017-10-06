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

import json
import unittest

import oneview_redfish_toolkit.api.status_mapping as status_mapping


class TestStatusMapping(unittest.TestCase):
    """Tests for StatusMapping class"""

    def test_mapping(self):
        """Test mapping OneView Status to Redfish Status.

            In this case self.server_hardware["status"] is equal to OK.
        """

        with open(
            'oneview_redfish_toolkit/mockups_oneview/ServerHardware.json'
        ) as f:
            server_hardware = json.load(f)

        redfish_state = \
            status_mapping.get_redfish_state(server_hardware["status"])

        self.assertEqual(redfish_state, "Enabled")

        redfish_health = \
            status_mapping.get_redfish_health(server_hardware["status"])

        self.assertEqual(redfish_health, "OK")
