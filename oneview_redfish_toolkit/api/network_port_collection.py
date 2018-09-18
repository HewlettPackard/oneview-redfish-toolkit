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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class NetworkPortCollection(RedfishJsonValidator):
    """Creates a Network Port Collection Redfish dict

        Populates self.redfish with some hardcoded NetworkPortCollection
        values and Oneview ServerHardware result.
    """

    SCHEMA_NAME = 'NetworkPortCollection'

    def __init__(self, server_hardware, device_id):
        """NetworkPortCollection constructor

            Populates self.redfish and calls _validate()

            Args:
                server_hardware: a server hardware dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        physical_ports = self.get_resource_by_id(
            server_hardware["portMap"]["deviceSlots"], "deviceNumber",
            device_id)["physicalPorts"]

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Network Port Collection"
        self.redfish["Members"] = list()

        for port in physical_ports:
            port_link = dict()
            port_link["@odata.id"] = \
                "/redfish/v1/Chassis/{}/NetworkAdapters/{}/NetworkPorts/{}" \
                .format(server_hardware["uuid"],
                        device_id, port["portNumber"])
            self.redfish["Members"].append(port_link)

        self.redfish["Members@odata.count"] = len(physical_ports)
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#NetworkPortCollection" \
            ".NetworkPortCollection"
        self.redfish["@odata.id"] = \
            "/redfish/v1/Chassis/{}/NetworkAdapters/{}/NetworkPorts" \
            .format(server_hardware["uuid"], device_id)

        self._validate()
