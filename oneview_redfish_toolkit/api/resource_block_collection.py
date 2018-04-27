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


class ResourceBlockCollection(RedfishJsonValidator):
    """Creates a ResourceBlock Collection Redfish dict

        Populates self.redfish with some hardcoded ResourceBlockCollection
        values and with the response of Oneview.
    """

    SCHEMA_NAME = 'ResourceBlockCollection'

    def __init__(self, server_hardware):
        """ResourceBlockCollection constructor

            Populates self.redfish with a hardcoded ResourceBlockCollection
            values and with the response of Oneview.
        """

        super().__init__(self.SCHEMA_NAME)

        self.server_hardware = server_hardware

        self.redfish["@odata.type"] = \
            "#ResourceBlockCollection.ResourceBlockCollection"
        self.redfish["Name"] = "Resource Block Collection"
        self.redfish["Members@odata.count"] = len(server_hardware)
        self.redfish["Members"] = list()
        self._set_redfish_members()
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ResourceBlockCollection" \
            ".ResourceBlockCollection"
        self.redfish["@odata.id"] = "/redfish/v1/CompositionService" \
            "/ResourceBlocks"

        self._validate()

    def _set_redfish_members(self):
        """Mounts the list of the ResourceBlock members

            Populates self.redfish["Members"] with the links to each Redfish
            ResourceBlock.
        """

        for server_hardware in self.server_hardware:
            resource_block = dict()

            resource_block["@odata.id"] = "/redfish/v1/CompositionService/" \
                "ResourceBlocks/" + server_hardware["uuid"]

            self.redfish["Members"].append(resource_block)
