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


class ChassisCollection(RedfishJsonValidator):
    """Creates a Chassis Collection Redfish dict

        Populates self.redfish with some hardcoded ChassisCollection
        values and with the response of Oneview with all server hardware,
        enclosures and racks resource.
    """

    SCHEMA_NAME = 'ChassisCollection'

    def __init__(self, server_hardware, enclosures, racks):
        """ChassisCollection constructor

            Populates self.redfish with a hardcoded ChassisCollection
            values and with the response of Oneview with all server hardware,
            enclosures and racks resource.

            Args:
                server_hardware: A list of dicts of server hardware.
                enclosures: A list of dicts of enclosures.
                racks: A list of dicts of racks.
        """

        super().__init__(self.SCHEMA_NAME)

        self.server_hardware = server_hardware
        self.enclosures = enclosures
        self.racks = racks

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "MultiBlade Enclosure Chassis Collection"
        self.redfish["Members@odata.count"] = self. \
            _get_redfish_members_length()
        self.redfish["Members"] = list()
        self._set_redfish_members()
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ChassisCollection" \
            ".ChassisCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis"

        self._validate()

    def _set_redfish_members(self):
        """Mounts the list of Redfish members

            Populates self.redfish["Members"] with the links to Redfish
            EnclosureChassis, BladeChassis and Rack.
        """

        self._set_resource_links(self.enclosures)
        self._set_resource_links(self.racks)
        self._set_resource_links(self.server_hardware)

    def _set_resource_links(self, oneview_resource):
        """Populates self.redfish["Members"] with the links resources"""

        for resource in oneview_resource:
            link_dict = collections.OrderedDict()
            link_dict["@odata.id"] = \
                "/redfish/v1/Chassis/" + resource["uuid"]
            self.redfish["Members"].append(link_dict)

    def _get_redfish_members_length(self):
        """Gets the length of redfish members"""

        return len(self.server_hardware) + len(self.enclosures) \
            + len(self.racks)
