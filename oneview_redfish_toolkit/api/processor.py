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
from oneview_redfish_toolkit.api.resource_block_collection \
    import ResourceBlockCollection
import oneview_redfish_toolkit.api.status_mapping as status_mapping


class Processor(RedfishJsonValidator):
    """Creates a Processor Redfish dict

        Populates self.redfish with some hardcoded Processor
        values and data retrieved from Oneview.
    """

    SCHEMA_NAME = 'Processor'

    def __init__(self, server_hardware, processor_id):
        """Processor constructor

            Populates self.redfish with the some common contents
            and data from OneView server hardware.

            Args:
                server_hardware: server hardware dict from OneView
                processor_id: processor identifier
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = processor_id
        self.redfish["Name"] = "Processor " + processor_id
        self.redfish["Status"] = dict()
        state, health = status_mapping.\
            get_redfish_server_hardware_status_struct(server_hardware)
        self.redfish["Status"]["State"] = state
        self.redfish["Status"]["Health"] = health
        self.redfish["ProcessorType"] = "CPU"
        self.redfish["Model"] = server_hardware["processorType"]
        self.redfish["MaxSpeedMHz"] = server_hardware["processorSpeedMhz"]
        self.redfish["TotalCores"] = server_hardware["processorCoreCount"]

        self._fill_links(server_hardware)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Processor.Processor"
        self.redfish["@odata.id"] = \
            ResourceBlockCollection.BASE_URI + "/" \
            + server_hardware["uuid"] + "/Systems/1/Processors/" + processor_id

        self._validate()

    def _fill_links(self, server_hardware):
        self.redfish["Links"] = dict()

        self.redfish["Links"]["Chassis"] = dict()
        self.redfish["Links"]["Chassis"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware["uuid"]
