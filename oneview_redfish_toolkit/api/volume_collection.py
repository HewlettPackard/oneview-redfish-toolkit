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
import collections
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class VolumeCollection(RedfishJsonValidator):

    """Populates the volumes of a server profile in redfish format"""

    SCHEMA_NAME = 'VolumeCollection'

    def __init__(self, server_profile):
        """VolumeCollections constructor

            Populates self.redfish and validates the result

            Args:
                server_profile: server profile object
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Storage Volume Collection"
        self.redfish["Description"] = "Storage Volume Collection"
        self.redfish["Members@odata.count"] = len(
            server_profile["localStorage"]["sasLogicalJBODs"]) + \
            len(server_profile["sanStorage"]["volumeAttachments"])

        self.redfish["Members"] = list()

        for i in range(len(server_profile["localStorage"]["sasLogicalJBODs"])):
            link_dict = collections.OrderedDict()
            link_dict["@odata.id"] = "/redfish/v1/Systems/" \
                + server_profile["uuid"] \
                + "/Storage/1/Volumes/" \
                + str(server_profile["localStorage"]
                      ["sasLogicalJBODs"][i]["id"])
            self.redfish["Members"].append(link_dict)

        for volume in server_profile["sanStorage"]["volumeAttachments"]:
            link_dict = collections.OrderedDict()
            volume_id = volume["volumeUri"].split("/")[-1]
            link_dict["@odata.id"] = "/redfish/v1/Systems/" \
                + server_profile["uuid"] \
                + "/Storage/1/Volumes/" \
                + volume_id
            self.redfish["Members"].append(link_dict)

        self.redfish["Oem"] = {}
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#VolumeCollection" \
            ".VolumeCollection"
        self.redfish["@odata.id"] = "/redfish/v1/Systems/" \
            + server_profile["uuid"] + "/Storage/1/Volumes"
        self._validate()
