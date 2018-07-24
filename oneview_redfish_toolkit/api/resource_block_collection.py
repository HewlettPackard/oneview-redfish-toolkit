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
    BASE_URI = '/redfish/v1/CompositionService/ResourceBlocks'

    def __init__(self,
                 server_hardware=[],
                 server_profile_templates=[],
                 drives=[]):
        """ResourceBlockCollection constructor

            Populates self.redfish with a hardcoded ResourceBlockCollection
            values and with the response of Oneview.
        """

        super().__init__(self.SCHEMA_NAME)

        self.members = server_hardware \
            + server_profile_templates \
            + drives

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Resource Block Collection"

        self.redfish["Members"] = list()
        self._fill_resource_block_list()
        self.redfish["Members@odata.count"] = len(self.redfish["Members"])

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ResourceBlockCollection" \
            ".ResourceBlockCollection"
        self.redfish["@odata.id"] = self.BASE_URI

        self._validate()

    def _fill_resource_block_list(self):
        """Mounts the list of the ResourceBlock members

            Populates self.redfish["Members"] with the links to ResourceBlocks.
        """

        for block in self.members:
            block_id = block.get("uuid", block["uri"].split("/")[-1])

            resource_block = dict()

            resource_block["@odata.id"] = self.BASE_URI + "/" + block_id

            self.redfish["Members"].append(resource_block)
