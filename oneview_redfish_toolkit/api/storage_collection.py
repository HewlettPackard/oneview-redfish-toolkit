# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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


class StorageCollection(RedfishJsonValidator):
    """Creates a Storage Collection Redfish dict

        Populates self.redfish with some hardcoded StorageCollection
        values
    """

    SCHEMA_NAME = 'StorageCollection'

    def __init__(self, uuid):
        """StorageCollection constructor

            Populates self.redfish with hardcoded StorageCollection
            values

            Args:
                UUID of server profile
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Storage Collection"
        self.redfish["Members@odata.count"] = 1
        self.redfish["Members"] = list()
        self.redfish["Members"].append(collections.OrderedDict())
        self.redfish["Members"][0]["@odata.id"] = \
            "/redfish/v1/Systems/" + uuid + "/Storage/1"
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#StorageCollection" \
            ".StorageCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Systems/" + uuid + "/Storage"
        self._validate()
