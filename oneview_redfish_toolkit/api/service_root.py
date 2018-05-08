#!./redfish-venv/bin/python
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

import collections
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator


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
        self.redfish["@odata.type"] = "#ServiceRoot.v1_2_0.ServiceRoot"
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
        self.redfish["EventService"] = collections.OrderedDict()
        self.redfish["EventService"]["@odata.id"] = \
            "/redfish/v1/EventService"
        self.redfish['Links'] = collections.OrderedDict()
        # self.redfish['Links']['Sessions'] = collections.OrderedDict()
        # self.redfish['Links']['Sessions']['@odata.id'] = \
        #    "/redfish/v1/SessionService/Sessions"
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ServiceRoot.ServiceRoot"
        self.redfish["@odata.id"] = "/redfish/v1/"
        self.redfish["@Redfish.Copyright"] = \
            "Copyright (2017) Hewlett Packard Enterprise Development LP"

        self._validate()
