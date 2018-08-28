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


class CapabilitiesObject(RedfishJsonValidator):
    """Creates a CapabilitiesObject Redfish dict

        Populates self.redfish with some hardcoded Capability
        values and with the response of OneView.
    """

    SCHEMA_NAME = 'ComputerSystem'
    BASE_URI = '/redfish/v1/Systems'

    def __init__(self, profile_template):
        """Capability constructor

            Populates self.redfish with some hardcoded Capability
            values and with the response of OneView.

            Args:
                profile_template: Oneview's Server profile templates dict
        """
        super().__init__(self.SCHEMA_NAME)

        self.profile_template = profile_template
        uuid = profile_template["uri"].split("/")[-1]

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = uuid
        self.redfish["Name"] = profile_template["name"]

        self.redfish["Description@Redfish.OptionalOnCreate"] = True
        self.redfish["Description@Redfish.UpdatableAfterCreate"] = True
        self.redfish["Id@Redfish.RequiredOnCreate"] = True
        self.redfish["Id@Redfish.AllowableValues"] = [uuid]
        self.redfish["Name@Redfish.RequiredOnCreate"] = True
        self.redfish["Name@Redfish.SetOnlyOnCreate"] = True
        self.redfish["Links@Redfish.RequiredOnCreate"] = True

        links = dict()
        links["ResourceBlocks@Redfish.RequiredOnCreate"] = True
        links["ResourceBlocks@Redfish.UpdatableAfterCreate"] = True
        self.redfish["Links"] = links

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ComputerSystem.ComputerSystem"
        self.redfish["@odata.id"] = "{}/{}".format(
            self.BASE_URI, uuid)

        self._validate()
