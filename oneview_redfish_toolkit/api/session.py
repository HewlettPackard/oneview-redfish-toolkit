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
from oneview_redfish_toolkit.api.session_collection import SessionCollection


class Session(RedfishJsonValidator):
    """Super class of Session Service

        Populates self.redfish with Session response.
    """

    SCHEMA_NAME = 'Session'

    def __init__(self, session_id):
        """Session constructor

            Populates self.redfish with Session response.

            Args:
                session_id: The session ID of the user logged in
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Session.Session"
        self.redfish["@odata.id"] = \
            SessionCollection.BASE_URI + "/" + str(session_id)
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = str(session_id)
        self.redfish["Name"] = "User Session"

        self._validate()
