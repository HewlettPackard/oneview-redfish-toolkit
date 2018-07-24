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


class ProcessorCollection(RedfishJsonValidator):
    """Creates a Processor Collection Redfish dict

        Populates self.redfish with some hardcoded ProcessorCollection
        values and with the server hardware response from OneView.
    """

    SCHEMA_NAME = 'ProcessorCollection'

    def __init__(self, server_hardware):
        """ProcessorCollection constructor

            Populates self.redfish with a hardcoded ProcessorCollection
            values and with the server hardware response from OneView.

            Args:
                server_hardware: Server hardware dict.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Processors Collection"

        self._fill_members(server_hardware)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ProcessorCollection.ProcessorCollection"
        self.redfish["@odata.id"] = \
            ResourceBlockCollection.BASE_URI + "/" \
            + server_hardware["uuid"] + "/Systems/1/Processors"

        self._validate()

    def _fill_members(self, server_hardware):
        processor_count = server_hardware["processorCount"]

        self.redfish["Members@odata.count"] = processor_count
        self.redfish["Members"] = list()

        for processor_id in range(processor_count):
            processor = dict()
            processor["@odata.id"] = \
                ResourceBlockCollection.BASE_URI + "/" \
                + server_hardware["uuid"] \
                + "/Systems/1/Processors/" + str(processor_id + 1)

            self.redfish["Members"].append(processor)
