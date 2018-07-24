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


class ResourceBlock(RedfishJsonValidator):
    """Creates a ResourceBlock Redfish dict

        Populates self.redfish with some hardcoded ResourceBlock
        values and data retrieved from OneView.
    """

    SCHEMA_NAME = 'ResourceBlock'
    BASE_URI = '/redfish/v1/CompositionService/ResourceBlocks'

    def __init__(self, uuid, oneview_resource):
        """ResourceBlock constructor

            Populates self.redfish with the some common contents
            and data from OneView resource.

            Args:
                uuid: OneView resource UUID
                oneview_resource: resource dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        self.uuid = uuid

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = uuid
        self.redfish["Name"] = oneview_resource["name"]

        # This object must be completed by each implementation
        self.redfish["CompositionStatus"] = dict()

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ResourceBlock.ResourceBlock"
        self.redfish["@odata.id"] = self.BASE_URI + "/" + uuid
