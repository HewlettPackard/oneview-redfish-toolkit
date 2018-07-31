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


class ZoneCollection(RedfishJsonValidator):
    """Creates a Zone Collection Redfish dict

        Populates self.redfish with some hardcoded ZoneCollection
        values and with the response of OneView.
    """

    SCHEMA_NAME = 'ZoneCollection'
    BASE_URI = '/redfish/v1/CompositionService/ResourceZones'

    def __init__(self, zone_ids):
        """ZoneCollection constructor

            Populates self.redfish with some hardcoded ZoneCollection
            values and with the response of OneView.

            Args:
                zone_ids: Zone ids based on Oneview data
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Resource Zone Collection"

        self.redfish["Members@odata.count"] = len(zone_ids)
        self.redfish["Members"] = list()
        self._fill_redfish_members(zone_ids)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ZoneCollection.ZoneCollection"
        self.redfish["@odata.id"] = \
            "/redfish/v1/CompositionService/ResourceZones"

        self._validate()

    def _fill_redfish_members(self, zone_ids):
        """Mounts the list of Redfish members

            Populates self.redfish["Members"] with the links
            to Redfish Resource Zones.
        """
        for zone_id in zone_ids:
            resource_zone = {
                "@odata.id": self.BASE_URI + "/" + zone_id
            }
            self.redfish["Members"].append(resource_zone)
