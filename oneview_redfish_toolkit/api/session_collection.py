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


class SessionCollection(RedfishJsonValidator):
    """Session Collection class

        Populates self.redfish with a list of active sessions.
    """

    BASE_URI = "/redfish/v1/SessionService/Sessions"
    SCHEMA_NAME = 'SessionCollection'

    def __init__(self, ids):
        """Session constructor

            Populates self.redfish with Session response.

            Args:
                ids: List with id of sessions
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#SessionCollection.SessionCollection"
        self.redfish["@odata.id"] = self.BASE_URI
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Active sessions"
        self.redfish["Members"] = [self._build_member(s_id) for s_id in ids]
        self.redfish["Members@odata.count"] = len(self.redfish["Members"])

        self._validate()

    def _build_member(self, session_id):
        return {"@odata.id": self.BASE_URI + "/" + str(session_id)}
