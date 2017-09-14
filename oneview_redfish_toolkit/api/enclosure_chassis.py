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

import re


class EnclosureChassis(RedfishJsonValidator):
    """Creates an Enclosure Chassis Redfish dict

         Populates self.redfish with some hardcoded Enclosure Chassis
         values and with the response of OneView enclosure.
    """

    SCHEMA_NAME = 'Chassis'

    def __init__(self, enclosure, environmental_configuration):
        """Enclosure Chassis constructor

        Populates self.redfish with hardcoded Enclosure Chassis
        values and with the response of OneView enclosure.

        Args:
            enclosure: An object containing the Oneview enclosure
            to create the Redfish JSON.

            environmental_configuration: An object having information
            about the rack that containing the enclosure.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = "#Chassis.v1_2_0.Chassis"
        self.redfish["Id"] = enclosure["uuid"]
        self.redfish["Name"] = enclosure["name"]
        self.redfish["ChassisType"] = "Enclosure"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = enclosure["enclosureModel"]
        self.redfish["SerialNumber"] = enclosure["serialNumber"]
        self.redfish["PartNumber"] = enclosure["partNumber"]
        self.redfish["IndicatorLED"] = self. \
            _map_indicator_led(enclosure["uidState"])
        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = enclosure["status"]
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["Links"]["Contains"] = list()
        self._set_links_to_computer_system(
            enclosure["deviceBays"])
        self.redfish["Links"]["ContainedBy"] = collections.OrderedDict()
        self.redfish["Links"]["ContainedBy"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + environmental_configuration["rackId"]
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Chassis.Chassis"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/MultiBladeEncl"

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

    def _set_links_to_computer_system(self, oneview_device_bays):
        """Mounts the list of Enclosure Links

            Populates self.redfish["Links"]["Contains"] with the links
            to all ComputerSystem chassis it contains.

            Args:
                oneview_device_bays: list of dicts containing information
                about devices and URI to OneView server hardwares.
        """

        computer_systems_uuid = self. \
            _filter_by_computer_system_uuid(oneview_device_bays)

        for computer_system_uuid in computer_systems_uuid:
            link_dict = collections.OrderedDict()
            link_dict["@odata.id"] = \
                "/redfish/v1/Chassis/" + computer_system_uuid
            self.redfish["Links"]["Contains"].append(link_dict)

    def _filter_by_computer_system_uuid(self, oneview_device_bays):
        """Return Computer Systems UUID

            Iterate over oneview_device_bays and filter by only UUIDs
            related to server hardwares.

            Args:
                oneview_device_bays: list of dicts containing information
                about devices and URI of OneView server hardwares.

            Returns:
                list: List of ComputerSystem UUID.
        """

        pattern = re.compile(r'\b[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-'
                             r'[A-Z0-9]{4}-[A-Z0-9]{12}\b')

        computer_system_uuid = list()

        for device_dict in oneview_device_bays:
            uri = device_dict["deviceUri"]

            if uri is not None:
                uuid = uri.split("/")[-1]

                if pattern.match(uuid):
                    computer_system_uuid.append(uuid)

        return computer_system_uuid
