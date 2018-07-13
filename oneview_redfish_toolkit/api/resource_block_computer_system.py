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

import collections

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection
import oneview_redfish_toolkit.api.status_mapping as status_mapping


class ResourceBlockComputerSystem(RedfishJsonValidator):
    """Creates a Resource Block Computer System Redfish dict

        Populates self.redfish with some predefined Computer System
        contents and with data retrieved from OneView
    """

    SCHEMA_NAME = 'ComputerSystem'

    def __init__(self, server_hardware):
        """ResourceBlock ComputerSystem constructor

            Populates self.redfish with the contents of server hardware dict.

            Args:
                server_hardware: server hardware dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        self.server_hardware = server_hardware

        self.redfish["@odata.type"] = "#ComputerSystem.v1_4_0.ComputerSystem"
        self.redfish["Id"] = server_hardware["uuid"]
        self.redfish["Name"] = server_hardware["name"]
        self.redfish["SystemType"] = "Physical"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = server_hardware["model"]
        self.redfish["SerialNumber"] = server_hardware["serialNumber"]
        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = \
            status_mapping.get_redfish_state(server_hardware["status"])
        self.redfish["Status"]["Health"] = \
            status_mapping.get_redfish_health(server_hardware["status"])

        self.redfish["PowerState"] = server_hardware["powerState"]
        self.redfish["BiosVersion"] = server_hardware["romVersion"]

        self.redfish["ProcessorSummary"] = collections.OrderedDict()
        self.redfish["ProcessorSummary"]['Count'] = \
            server_hardware["processorCount"]
        self.redfish["ProcessorSummary"]["Model"] = \
            server_hardware["processorType"]
        self.redfish["Processors"] = dict()
        self.redfish["Processors"]["@odata.id"] = \
            ResourceBlockCollection.BASE_URI + "/" \
            + server_hardware["uuid"] + "/Systems/1/Processors"

        self.redfish["MemorySummary"] = collections.OrderedDict()
        self.redfish["MemorySummary"]["TotalSystemMemoryGiB"] = \
            server_hardware["memoryMb"] / 1024

        self._fill_links()

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ComputerSystem.ComputerSystem"
        self.redfish["@odata.id"] = \
            ResourceBlockCollection.BASE_URI + "/" \
            + server_hardware["uuid"] \
            + "/Systems/1"

        self._validate()

    def _fill_links(self):
        self.redfish["Links"] = collections.OrderedDict()

        self.redfish["Links"]["Chassis"] = list()
        chassi = dict()
        chassi["@odata.id"] = "/redfish/v1/Chassis/{}" \
            .format(self.server_hardware["uuid"])
        self.redfish["Links"]["Chassis"].append(chassi)

        self.redfish["Links"]["ManagedBy"] = list()
        manager = dict()
        manager["@odata.id"] = "/redfish/v1/Managers/{}" \
            .format(self.server_hardware["uuid"])
        self.redfish["Links"]["ManagedBy"].append(manager)
