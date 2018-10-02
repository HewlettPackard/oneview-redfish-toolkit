#!./redfish-venv/bin/python
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

import collections

from oneview_redfish_toolkit.api.event_service import EventService
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit.api.session_service import SessionService
from oneview_redfish_toolkit import config


class ServiceRoot(RedfishJsonValidator):
    """Creates a hardcoded ServiceRoot redfish dict

        Populates self.redfish with a hardcoded ServiceRoot values for
        a BladeSystem

    """

    SCHEMA_NAME = 'ServiceRoot'

    def __init__(self, oneview_uuid):
        """Constructor

            Populates self.redfish with a hardcoded ServiceRoot values for
            a BladeSystem. Validates the self.redfish content against the
            ServiceRoot schema

            Parameters:
                oneview_uuid: string containing OneView's UUID
        """

        super().__init__(self.SCHEMA_NAME)
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = "RootService"
        self.redfish["Name"] = "Root Service"
        self.redfish["RedfishVersion"] = "1.2.0"
        self.redfish["UUID"] = oneview_uuid
        self.redfish["Systems"] = collections.OrderedDict()
        self.redfish["Systems"]["@odata.id"] = "/redfish/v1/Systems"
        self.redfish["Chassis"] = collections.OrderedDict()
        self.redfish["Chassis"]["@odata.id"] = "/redfish/v1/Chassis"
        self.redfish["Managers"] = collections.OrderedDict()
        self.redfish["Managers"]["@odata.id"] = "/redfish/v1/Managers"
        self.redfish["CompositionService"] = collections.OrderedDict()
        self.redfish["CompositionService"]["@odata.id"] = \
            "/redfish/v1/CompositionService"

        self.add_event_service_api()
        self.add_session_service_endpoints()

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ServiceRoot.ServiceRoot"
        self.redfish["@odata.id"] = "/redfish/v1/"
        self.redfish["@Redfish.Copyright"] = \
            "Copyright (2017-2018) Hewlett Packard Enterprise Development LP"

        self._validate()

    def add_event_service_api(self):
        self.redfish["EventService"] = {"@odata.id": EventService.BASE_URI}

    def add_session_service_endpoints(self):
        self.redfish["SessionService"] = {"@odata.id": SessionService.BASE_URI}
        self.redfish["Links"] = {"Sessions": {}}
        if config.auth_mode_is_session():
            self.redfish['Links']['Sessions']['@odata.id'] = \
                SessionService.BASE_URI + "/Sessions"
