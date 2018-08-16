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


class VLanNetworkInterfaceCollection(RedfishJsonValidator):
    """Creates a VLanNetworkInterfaceCollection Redfish dict

        Populates self.redfish with network set data retrieved
        from OneView
    """

    SCHEMA_NAME = 'VLanNetworkInterfaceCollection'

    def __init__(self, network_set, endpoint):
        """VLanNetworkInterfaceCollection constructor

            Populates self.redfish with NetworkSet
            data retrieved from OneView.

            Args:
                network_set: Network Set dict from OneView
                endpoint: endpoint uri from original REST
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = network_set["name"]
        self.redfish["Members@odata.count"] = len(network_set["networkUris"])
        self.redfish["Members"] = list()
        self._set_vlans_to_network_collection(endpoint,
                                              network_set["networkUris"])

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#VLanNetworkInterfaceCollection"
        self.redfish["@odata.id"] = endpoint

        self._validate()

    def _set_vlans_to_network_collection(self, endpoint,
                                         ethernet_networks_uri):
        """Mounts the list of VLans Links

            Populates self.redfish["Members"] with the links
            to all VLanNetworkInterfaces it contains.

            Args:
                ethernet_networks_uri: list of URIs for the
                VLanNetworkInterfaces.
                endpoint: endpoint uri from original REST.
        """

        for ethernet_uri in ethernet_networks_uri:
            vlan = dict()
            vlan["@odata.id"] = endpoint + "/" + ethernet_uri.split("/")[-1]
            self.redfish["Members"].append(vlan)
