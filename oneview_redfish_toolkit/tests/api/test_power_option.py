# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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
from oneview_redfish_toolkit.api.util.power_option import OneViewPowerOption
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestPowerOption(BaseTest):
    """Tests for Power Option class"""

    def setUp(self):

        with open(
                'oneview_redfish_toolkit/mockups/oneview/ServerHardware.json'
        ) as f:
            self.server_hardware = json.load(f)

    def test_power_option_valid_reset_actions(self):
        """Tests to get OneView Reset Actions with valid keys"""

        expected_oneview_power_options = {
            "On": {
                "powerState": "On",
            },
            "ForceOff": {
                "powerState": "Off",
                "powerControl": "PressAndHold"
            },
            "GracefulShutdown": {
                "powerState": "Off",
                "powerControl": "MomentaryPress"
            },
            "GracefulRestart": {
                "powerState": "On",
                "powerControl": "Reset"
            },
            "ForceRestart": {
                "powerState": "On",
                "powerControl": "ColdBoot"
            },
            "PushPowerButton": {
                "powerState": "Off",
                "powerControl": "MomentaryPress",
            }
        }

        reset_types = ["On", "ForceOff", "GracefulShutdown",
                       "GracefulRestart", "ForceRestart", "PushPowerButton"]

        for reset_type in reset_types:
            result = OneViewPowerOption.get_oneview_power_configuration(
                self.server_hardware, reset_type)
            self.assertEqual(
                result, expected_oneview_power_options[reset_type])

    def test_power_option_invalid_reset_actions(self):
        """Tests raises OneviewRedFishError exception for invalid keys"""

        reset_types = ["ForceOn", "Nmi"]

        for reset_type in reset_types:
            self.assertRaises(
                OneViewRedfishError,
                OneViewPowerOption.get_oneview_power_configuration,
                self.server_hardware, reset_type)

    def test_power_option_unmapped_reset_key(self):
        """Tests raises OneviewRedFishError exception for unmapped keys"""

        self.assertRaises(
            OneViewRedfishError,
            OneViewPowerOption.get_oneview_power_configuration,
            self.server_hardware, "INVALID_KEY")
