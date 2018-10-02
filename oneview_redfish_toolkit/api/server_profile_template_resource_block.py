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

from oneview_redfish_toolkit.api.resource_block import ResourceBlock
from oneview_redfish_toolkit.api.zone_collection import ZoneCollection


class ServerProfileTemplateResourceBlock(ResourceBlock):
    """Creates a ResourceBlock Redfish dict for Server Profile Template

        Populates self.redfish with some hardcoded ResourceBlock
        values and with Server Profile Template data retrieved from OneView.
    """

    def __init__(self, uuid, server_profile_template, zone_ids):
        """ServerProfileTemplateResourceBlock constructor

            Populates self.redfish with the contents of server profile
            template dict.

            Args:
                uuid: server profile template UUID
                server_profile_template: OneView server profile template
                zone_ids: Ids of Zones that this resource block belongs to
        """
        super().__init__(uuid, server_profile_template)

        self.server_profile_template = server_profile_template

        self.redfish["ResourceBlockType"] = ["Network"]
        self.redfish["CompositionStatus"]["SharingCapable"] = True
        self.redfish["CompositionStatus"]["SharingEnabled"] = True
        self.redfish["CompositionStatus"]["CompositionState"] = "Unused"

        self._fill_ethernet_networks()

        self.redfish["Links"] = dict()
        self.redfish["Links"]["Zones"] = list()

        self._fill_link_members(zone_ids)

    def _fill_link_members(self, zone_ids):
        for zone_id in zone_ids:
            zone = {
                "@odata.id": ZoneCollection.BASE_URI + "/" + zone_id
            }
            self.redfish["Links"]["Zones"].append(zone)

    def _fill_ethernet_networks(self):
        self.redfish["EthernetInterfaces"] = list()

        connSettings = self.server_profile_template["connectionSettings"]

        for conn in connSettings["connections"]:
            if "Ethernet" == conn["functionType"]:
                network = dict()
                network["@odata.id"] = self.BASE_URI + "/" + self.uuid \
                    + "/EthernetInterfaces/" + str(conn["id"])

                self.redfish["EthernetInterfaces"].append(network)

        self.redfish["EthernetInterfaces@odata.count"] = \
            len(self.redfish["EthernetInterfaces"])
