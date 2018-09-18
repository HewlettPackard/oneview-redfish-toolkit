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

import copy

from oneview_redfish_toolkit.api.errors import OneViewRedfishError


RESET_ALLOWABLE_VALUES_LIST = ["On", "ForceOff", "GracefulShutdown",
                               "GracefulRestart", "ForceRestart",
                               "PushPowerButton"]
RESET_INVALID_VALUES_LIST = ["ForceOn", "Nmi"]
POWER_STATE_MAP = {
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
        "powerControl": "MomentaryPress"
    }
}


class OneViewPowerOption(object):

    @staticmethod
    def get_power_state_by_reset_type(reset_type):
        try:
            return copy.copy(POWER_STATE_MAP[reset_type])
        except Exception:
            raise OneViewRedfishError({
                "errorCode": "INVALID_INFORMATION",
                "message": "There is no mapping for {} on the OneView".format(
                    reset_type
                )})

    @staticmethod
    def get_oneview_power_configuration(server_hardware, reset_type):
        """Maps Redfish's power options to OneView's power option

            Maps the known Redfish power options to OneView Power option.
            If a unknown power option shows up it will raise an Exception.

            Args:
                server_hardware: List containing all Oneview's server
                hardware.
                reset_type: Redfish power option.

            Returns:
                dict: Dict with OneView power configuration.

            Exception:
                OneViewRedfishError: raises an exception if
                reset_type is an unmapped value.
        """
        if reset_type in RESET_INVALID_VALUES_LIST:
            raise OneViewRedfishError({
                "errorCode": "NOT_IMPLEMENTED",
                "message": "{} not mapped to OneView".format(reset_type)})

        power_state_map = OneViewPowerOption.\
            get_power_state_by_reset_type(reset_type)

        if reset_type == "PushPowerButton":
            if server_hardware["powerState"] == "On":
                power_state_map["powerState"] = "Off"
            else:
                power_state_map["powerState"] = "On"

        return power_state_map
