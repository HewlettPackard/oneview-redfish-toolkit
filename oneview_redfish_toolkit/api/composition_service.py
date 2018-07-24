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


class CompositionService(RedfishJsonValidator):
    """Creates a Composition Service Redfish dict

        Populates self.redfish with some hardcoded CompositionService
        values and with information fetched from OneView.
    """

    SCHEMA_NAME = 'CompositionService'

    def __init__(self):
        """CompositionService constructor

            Populates self.redfish with some hardcoded CompositionService
            values and with information fetched from OneView to build the
            ResourceBlocks and ResouceZones.
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = "CompositionService"
        self.redfish["Name"] = "Composition Service"

        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = "OK"

        self.redfish["ServiceEnabled"] = True

        self.redfish["ResourceBlocks"] = collections.OrderedDict()
        self.redfish["ResourceBlocks"]["@odata.id"] = \
            "/redfish/v1/CompositionService/ResourceBlocks"

        self.redfish["ResourceZones"] = collections.OrderedDict()
        self.redfish["ResourceZones"]["@odata.id"] = \
            "/redfish/v1/CompositionService/ResourceZones"

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#CompositionService.CompositionService"
        self.redfish["@odata.id"] = "/redfish/v1/CompositionService"
        self._validate()
