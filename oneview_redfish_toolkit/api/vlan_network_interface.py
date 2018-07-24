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


class VLanNetworkInterface(RedfishJsonValidator):
    """Creates a VLanNetworkInterface Redfish dict

        Populates self.redfish with ethernet network data retrieved
        from OneView
    """

    SCHEMA_NAME = 'VLanNetworkInterface'

    def __init__(self, ethernet_network, endpoint):
        """VLanNetworkInterface constructor

            Populates self.redfish with some hardcoded VLanNetworkInterface
            values and with Ethernet Network data retrieved from OneView.

            Args:
                network: Ethernet network dict from OneView
                endpoint: endpoint uri from original REST
        """

        super().__init__(self.SCHEMA_NAME)

        ethernet_network_id = \
            ethernet_network["uri"].split("/")[-1]

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = ethernet_network_id
        self.redfish["Name"] = ethernet_network["name"]
        self.redfish["VLANEnable"] = True
        self.redfish["VLANId"] = ethernet_network["vlanId"]
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#VLanNetworkInterface"
        self.redfish["@odata.id"] = endpoint

        self._validate()
