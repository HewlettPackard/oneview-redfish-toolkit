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
from oneview_redfish_toolkit.api.chassis \
    import Chassis

import re


class EnclosureChassis(Chassis):
    """Creates an Enclosure Chassis Redfish dict

         Populates self.redfish with some hardcoded Enclosure Chassis
         values and with the response of OneView enclosure resources.
    """

    def __init__(self, enclosure, environmental_configuration, manager_uuid):
        """Enclosure Chassis constructor

        Populates self.redfish with hardcoded Enclosure Chassis
        values and with the response of OneView enclosure.

        Args:
            enclosure: An object containing the Oneview enclosure
            to create the Redfish JSON.

            environmental_configuration: An object having information
            about the rack that containing the enclosure.
            manager_uuid: Oneview's current manager uuid.
        """

        super().__init__(enclosure)

        self.redfish["ChassisType"] = "Enclosure"
        self.redfish["Model"] = enclosure["enclosureModel"]
        self.redfish["IndicatorLED"] = self. \
            _map_indicator_led(enclosure["uidState"])
        self.redfish["Links"]["Contains"] = list()
        self._set_links_to_computer_system(
            enclosure["deviceBays"])
        self.redfish["Links"]["ManagedBy"] = list()
        if manager_uuid:
            self.redfish["Links"]["ManagedBy"].append(
                collections.OrderedDict())
            self.redfish["Links"]["ManagedBy"][0]["@odata.id"] = \
                "/redfish/v1/Managers/" + manager_uuid
        self.redfish["Links"]["ContainedBy"] = collections.OrderedDict()
        self.redfish["Links"]["ContainedBy"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + environmental_configuration["rackId"]

        self._validate()

    def _set_links_to_computer_system(self, oneview_device_bays):
        """Mounts the list of Enclosure Links

            Populates self.redfish["Links"]["Contains"] with the links
            to all ComputerSystem chassis it contains.

            Args:
                oneview_device_bays: list of dicts containing information
                about devices and URI to OneView server hardware.
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
            related to server hardware.

            Args:
                oneview_device_bays: list of dicts containing information
                about devices and URI of OneView server hardware.

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
