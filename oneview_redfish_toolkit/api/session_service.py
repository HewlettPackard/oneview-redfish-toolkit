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
from oneview_redfish_toolkit import config


class SessionService(RedfishJsonValidator):
    """Creates a Session Service dict

        Populates self.redfish with SessionService values.
    """

    SCHEMA_NAME = 'SessionService'
    BASE_URI = '/redfish/v1/SessionService'

    def __init__(self):
        """Constructor

            Populates self.redfish with SessionService response.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["@odata.context"] = "/redfish/v1/$metadata" \
            "#SessionService.SessionService"
        self.redfish["@odata.id"] = self.BASE_URI

        self.redfish["Id"] = "SessionService"
        self.redfish["Name"] = "Session Service"
        self.redfish["Description"] = "Session service"

        # Enable Session Service only when authentication mode is session
        if config.auth_mode_is_session():
            self.redfish["ServiceEnabled"] = True
            self.redfish["Sessions"] = {
                "@odata.id": self.BASE_URI + "/Sessions"
            }
        else:
            self.redfish["ServiceEnabled"] = False

        self._validate()
