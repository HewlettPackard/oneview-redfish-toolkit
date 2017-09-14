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

import collections
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Chassis(RedfishJsonValidator):
    """Creates a Chassis Redfish dict

         Populates self.redfish with some hardcoded Chassis values and
         with the response of OneView hardware resources.
    """

    SCHEMA_NAME = 'Chassis'

    def __init__(self, hardware):
        """Chassis constructor

        Populates self.redfish with hardcoded Chassis values
        and with the response of OneView server hardware

        Args:
            hardware: An object containing hardware to
                      create the Redfish JSON.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = \
            "#Chassis.v1_5_0.Chassis"
        self.redfish["Id"] = hardware["uuid"]
        self.redfish["Name"] = hardware["name"]
        self.redfish["ChassisType"] = "Blade"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = hardware["model"]
        self.redfish["SerialNumber"] = hardware["serialNumber"]
        self.redfish["IndicatorLED"] = self. \
            _map_indicator_led(hardware["uidState"])
        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = hardware["status"]
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["Links"]["ComputerSystems"] = list()
        self.redfish["Links"]["ComputerSystems"] \
            .append(collections.OrderedDict())
        self.redfish["Links"]["ComputerSystems"][0]["@odata.id"] = \
            "/redfish/v1/Systems/" + hardware['uuid']

        self._validate()

    def _map_indicator_led(self, uid_state):
        """Maps Oneview's uid state to Redfish's indicator led.

            Maps the known OneView uid state to Redfish indicator led.
            If a unknown uid state shows up it will be mapped to Unknown.

            Args:
                uid_state: Uid state of Oneview.

            Returns:
                string: Redfish indicator led.
        """

        redfish_oneview_indicator_led_map = dict()
        redfish_oneview_indicator_led_map["On"] = "Lit"
        redfish_oneview_indicator_led_map["Off"] = "Off"
        redfish_oneview_indicator_led_map["Blink"] = "Blinking"

        try:
            return redfish_oneview_indicator_led_map[uid_state]
        except Exception:
            return "Unknown"
