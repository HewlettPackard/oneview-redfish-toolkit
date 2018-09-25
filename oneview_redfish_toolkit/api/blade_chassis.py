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
from oneview_redfish_toolkit.api.chassis import Chassis
from oneview_redfish_toolkit.api.computer_system import ComputerSystem
from oneview_redfish_toolkit.api.util.power_option import \
    RESET_ALLOWABLE_VALUES_LIST


class BladeChassis(Chassis):
    """Creates a Blade Chassis Redfish dict

         Populates self.redfish with some hardcoded Chassis values and
         with the response of OneView server hardware resources.
    """

    def __init__(self, server_hardware, manager_uuid):
        """BladeChassis constructor

        Populates self.redfish with hardcoded Chassis values
        and with the response of OneView server hardware.

        Args:
            server_hardware: An object containing hardware to
                      create the Redfish JSON.
            manager_uuid: Oneview's current manager uuid.
        """

        super().__init__(server_hardware)

        self.redfish["ChassisType"] = "Blade"
        self.redfish["Model"] = server_hardware["model"]
        self.redfish["IndicatorLED"] = self. \
            _map_indicator_led(server_hardware["uidState"])

        self.redfish["Links"]["ComputerSystems"] = list()

        server_profile_uri = server_hardware["serverProfileUri"]
        if server_profile_uri:
            system_id = server_profile_uri.split("/")[-1]
            self.redfish["Links"]["ComputerSystems"].append(
                {
                    "@odata.id": ComputerSystem.BASE_URI + "/" + system_id
                }
            )

        self.redfish["Links"]["ManagedBy"] = list()
        if manager_uuid:
            self.redfish["Links"]["ManagedBy"].append(
                collections.OrderedDict())
            self.redfish["Links"]["ManagedBy"][0]["@odata.id"] = \
                "/redfish/v1/Managers/" + manager_uuid

        if server_hardware["locationUri"] is not None:
            self.redfish["Links"]["ContainedBy"] = collections.OrderedDict()
            self.redfish["Links"]["ContainedBy"]["@odata.id"] = \
                "/redfish/v1/Chassis/" \
                + server_hardware["locationUri"].split("/")[-1]

        self.redfish["NetworkAdapters"] = dict()
        self.redfish["NetworkAdapters"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"] + \
            "/NetworkAdapters/"

        self.redfish["Actions"] = collections.OrderedDict()
        self.redfish["Actions"]["#Chassis.Reset"] = \
            collections.OrderedDict()
        self.redfish["Actions"]["#Chassis.Reset"]["target"] = \
            "/redfish/v1/Chassis" + "/" + \
            server_hardware["uuid"] + \
            "/Actions/Chassis.Reset"
        self.redfish["Actions"]["#Chassis.Reset"][
            "ResetType@Redfish.AllowableValues"] = \
            RESET_ALLOWABLE_VALUES_LIST

        self._validate()
