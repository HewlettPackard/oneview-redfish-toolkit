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

import collections

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
import oneview_redfish_toolkit.api.status_mapping as status_mapping


class Chassis(RedfishJsonValidator):
    """Super class of Chassis resources

         Populates self.redfish with common value between Enclosure,
         Rack and Blade.
    """

    SCHEMA_NAME = 'Chassis'

    def __init__(self, oneview_resource):
        """Chassis constructor

        Populates self.redfish with common value between Enclosure,
         Rack and Blade.

        Args:
            oneview_resource: An object some oneview_resource (ServerHardware,
            Enclosure or Rack) to create the Redfish JSON.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = oneview_resource["uuid"]
        self.redfish["Name"] = oneview_resource["name"]
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["SerialNumber"] = oneview_resource["serialNumber"]
        self.redfish["PartNumber"] = oneview_resource["partNumber"]
        self.redfish["Status"] = collections.OrderedDict()
        state, health = status_mapping.\
            get_redfish_server_hardware_status_struct(oneview_resource)
        self.redfish["Status"]["State"] = state
        self.redfish["Status"]["Health"] = health
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Chassis.Chassis"
        self.redfish["@odata.id"] = \
            "/redfish/v1/Chassis/" + oneview_resource['uuid']
        self.redfish["Thermal"] = collections.OrderedDict()
        self.redfish["Thermal"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + oneview_resource['uuid'] + "/Thermal"

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
            return None
