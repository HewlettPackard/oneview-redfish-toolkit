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

from oneview_redfish_toolkit.api.chassis import Chassis


class RackChassis(Chassis):
    """Creates a Rack Chassis Redfish dict

         Populates self.redfish with some hardcoded Rack Chassis
         values and with the response of OneView Rack.
    """

    def __init__(self, rack):
        """Rack Chassis constructor

        Populates self.redfish with hardcoded Rack Chassis
        values and with the response of OneView rack.

        Args:
            rack: An object containing the Oneview rack
            to create the Redfish JSON.
        """

        super().__init__(rack)

        self.redfish["ChassisType"] = "Rack"
        self.redfish["Model"] = rack["model"]
        self.redfish["Links"]["Contains"] = list()
        for enc in rack["rackMounts"]:
            self.redfish["Links"]["Contains"].append({
                "@odata.id": '/redfish/v1/Chassis/' +
                enc['mountUri'].split('/')[-1]
            })

        self._validate()
