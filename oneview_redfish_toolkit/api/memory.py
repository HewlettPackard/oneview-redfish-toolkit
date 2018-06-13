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


class Memory(RedfishJsonValidator):
    """Creates a Memory Redfish dict

        Populates self.redfish with some hardcoded Memory
        values and data retrieved from Oneview.
    """

    SCHEMA_NAME = 'Memory'

    def __init__(self, uuid, server_hardware):
        """Memory constructor

            Populates self.redfish with the some common contents
            and data from OneView server hardware resource.

            Args:
                uuid: server hardware UUID
                server_hardware: resource dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        self.server_hardware = server_hardware

        self.redfish["@odata.type"] = "#Memory.v1_2_0.Memory"
        self.redfish["Id"] = "1"
        self.redfish["Name"] = "Memory 1"
        self.redfish["Status"] = dict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = "OK"
        self.redfish["CapacityMiB"] = server_hardware["memoryMb"]

        self.fill_links()

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Memory.Memory"
        self.redfish["@odata.id"] = \
            "/redfish/v1/CompositionService/ResourceBlocks/" \
            + uuid + "/Memory/1"

        self._validate()

    def fill_links(self):
        self.redfish["Links"] = dict()

        self.redfish["Links"]["Chassis"] = dict()
        self.redfish["Links"]["Chassis"]["@odata.id"] = \
            "/redfish/v1/Chassis/" + self.server_hardware["uuid"]
