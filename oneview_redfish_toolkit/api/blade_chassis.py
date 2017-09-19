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
from oneview_redfish_toolkit.api.chassis import Chassis


class BladeChassis(Chassis):
    """Creates a Blade Chassis Redfish dict

         Populates self.redfish with some hardcoded Chassis values and
         with the response of OneView server hardware resources.
    """

    def __init__(self, server_hardware):
        """BladeChassis constructor

        Populates self.redfish with hardcoded Chassis values
        and with the response of OneView server hardware.

        Args:
            server_hardware: An object containing hardware to
                      create the Redfish JSON.
        """

        super().__init__(server_hardware)

        self.redfish["ChassisType"] = "Blade"
        self.redfish["Model"] = server_hardware["model"]
        self.redfish["IndicatorLED"] = self. \
            _map_indicator_led(server_hardware["uidState"])
        self.redfish["Links"]["ComputerSystems"] = list()
        self.redfish["Links"]["ComputerSystems"] \
            .append(collections.OrderedDict())
        self.redfish["Links"]["ComputerSystems"][0]["@odata.id"] = \
            "/redfish/v1/Systems/" + server_hardware['uuid']
        if server_hardware["locationUri"] is not None:
            self.redfish["Links"]["ContainedBy"] = collections.OrderedDict()
            self.redfish["Links"]["ContainedBy"]["@odata.id"] = "/redfish/v1/Chassis/" \
                + server_hardware["locationUri"].split("/")[-1]
        self.redfish["Thermal"] = collections.OrderedDict()
        self.redfish["Thermal"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware['uuid'] + "/Thermal"

        self._validate()
