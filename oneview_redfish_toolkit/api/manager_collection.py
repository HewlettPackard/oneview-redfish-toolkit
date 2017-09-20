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

import collections
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class ManagerCollection(RedfishJsonValidator):
    """Creates a Manager Collection Redfish dict

        Populates self.redfish with some hardcoded ManagerCollection
        values and with the response of Oneview with all server hardware,
        enclosures resource.
    """

    SCHEMA_NAME = 'ManagerCollection'

    def __init__(self, server_hardware, enclosures):
        """ChassisCollection constructor

            Populates self.redfish with a hardcoded ChassisCollection
            values and with the response of Oneview with all server hardware,
            enclosures resource.

            Args:
                server_hardware: A list of dicts of server hardware.
                enclosures: A list of dicts of enclosures.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = "#ManagerCollection.ManagerCollection"
        self.redfish["Name"] = "Manager Collection"
        self.redfish["Members@odata.count"] = \
            len(server_hardware) + len(enclosures)
        self.redfish["Members"] = list()
        self._set_resource_links(enclosures)
        self._set_resource_links(server_hardware)
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ManagerCollection.ManagerCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Managers"

        self._validate()

    def _set_resource_links(self, oneview_resource):
        """Populates self.redfish["Members"] with the links resources"""

        for resource in oneview_resource:
            link_dict = collections.OrderedDict()
            link_dict["@odata.id"] = \
                "/redfish/v1/Managers/" + resource["uuid"]
            self.redfish["Members"].append(link_dict)
