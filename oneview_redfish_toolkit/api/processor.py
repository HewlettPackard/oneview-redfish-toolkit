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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Processor(RedfishJsonValidator):
    """Creates a Processor Redfish dict

        Populates self.redfish with some hardcoded Processor
        values and data retrieved from Oneview.
    """

    SCHEMA_NAME = 'Processor'

    def __init__(self, uuid, id, server_hardware):
        """Processor constructor

            Populates self.redfish with the some common contents
            and data from OneView server hardware resource.

            Args:
                uuid: server hardware UUID
                id: processor identifier
                server_hardware: resource dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        self.server_hardware = server_hardware

        self.redfish["@odata.type"] = "#Processor.v1_1_0.Processor"
        self.redfish["Id"] = id
        self.redfish["Name"] = "Processor " + id
        self.redfish["Status"] = dict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = "OK"
        self.redfish["ProcessorType"] = "CPU"
        self.redfish["Model"] = server_hardware["processorType"]
        self.redfish["MaxSpeedMHz"] = server_hardware["processorSpeedMhz"]
        self.redfish["TotalCores"] = server_hardware["processorCoreCount"]

        self.fill_links()

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Processor.Processor"
        self.redfish["@odata.id"] = \
            "/redfish/v1/CompositionService/ResourceBlocks/" \
            + uuid + "/Processors/" + id

        self._validate()

    def fill_links(self):
        self.redfish["Links"] = dict()

        self.redfish["Links"]["Chassis"] = dict()
        self.redfish["Links"]["Chassis"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + self.server_hardware["uuid"]
