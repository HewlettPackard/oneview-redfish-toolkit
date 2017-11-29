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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Session(RedfishJsonValidator):
    """Super class of Session Service

        Populates self.redfish with Session response.
    """

    SCHEMA_NAME = 'Session'

    def __init__(self, username):
        """Session constructor

            Populates self.redfish with Session response.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Session.Session"
        self.redfish["@odata.id"] = "/redfish/v1/SessionService/Sessions/1"
        self.redfish["@odata.type"] = "#Session.v1_0_0.Session"
        self.redfish["Id"] = "1"
        self.redfish["Name"] = "User Session"
        self.redfish["Description"] = "User Session"
        self.redfish["UserName"] = username

        self._validate()
