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


class EventService(RedfishJsonValidator):
    """Creates a Event Service dict

        Populates self.redfish with some hardcoded EventService
        values and with the response from OneView.
    """

    SCHEMA_NAME = 'EventService'

    def __init__(self):
        """Manager constructor

            Populates self.redfish with some hardcoded EventService
            values and with the response from OneView.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = "#EventService.v1_0_4.EventService"
        self.redfish["Id"] = "1"
        self.redfish["Description"] = "Event Subscription service"
        self.redfish["Name"] = "Event Service"
        self.redfish["@odata.context"] = "/redfish/v1/$metadata#EventService"
        self.redfish["@odata.id"] = "/redfish/v1/EventService/"
        # self.redfish["Type"] = "EventService.1.0.4"
        # self.redfish["links"] = dict()
        # self.redfish["links"]["Subscriptions"] = dict()
        # self.redfish["links"]["Subscriptions"]["href"] = \
        #     "/redfish/v1/EventService/EventSubscriptions/"
        # self.redfish["links"]["self"] = dict()
        # self.redfish["links"]["self"]["href"] = "/redfish/v1/EventService/"
        self.redfish["Subscriptions"] = dict()
        self.redfish["Subscriptions"]["@odata.id"] = \
            "/redfish/v1/EventService/EventSubscriptions/"
        self.redfish["EventTypesForSubscription"] = \
            ["StatusChange", "ResourceUpdated", "ResourceAdded",
             "ResourceRemoved", "Alert"]

        # All information bellow is hard-coded
        # until we decide where to find it
        self.redfish["Status"] = dict()
        self.redfish["Status"]["Health"] = "OK"
        # self.redfish["Status"]["HealthRollUp"] = "OK"
        self.redfish["Status"]["State"] = "Enabled"

        self._validate()
