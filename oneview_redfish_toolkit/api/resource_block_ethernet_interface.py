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


class ResourceBlockEthernetInteface(RedfishJsonValidator):
    """Creates a Ethernet Interface Redfish dict

        Populates self.redfish with EthernetInterface data retrieved
        from OneView
    """

    SCHEMA_NAME = 'EthernetInterface'

    def __init__(self, server_profile_template, connection, network):

        super().__init__(self.SCHEMA_NAME)

        server_profile_template_id = \
            server_profile_template["uri"].split("/")[-1]

        self.redfish["@odata.type"] = \
            "#EthernetInterface.v1_3_0.EthernetInterface"
        self.redfish["Id"] = server_profile_template_id
        self.redfish["Name"] = network["name"]
        self.redfish["SpeedMbps"] = int(connection["requestedMbps"])
        self.redfish["VLAN"] = dict()
        self.redfish["VLAN"]["VLANEnable"] = True
        self.redfish["VLAN"]["VLANId"] = network["vlanId"]

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EthernetInterface.EthernetInterface"
        self.redfish["@odata.id"] = \
            "/redfish/v1/CompositionService/ResourceBlocks/" \
            + server_profile_template_id \
            + "/EthernetInterfaces/" \
            + str(connection["id"])

        self._validate()
