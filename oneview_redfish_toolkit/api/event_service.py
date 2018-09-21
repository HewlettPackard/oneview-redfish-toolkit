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
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import util


class EventService(RedfishJsonValidator):
    """Creates a Event Service dict

        Populates self.redfish with EventService values.
    """

    SCHEMA_NAME = 'EventService'
    BASE_URI = '/redfish/v1/EventService'

    def __init__(self, delivery_retry_attempts, delivery_retry_interval):
        """Constructor

            Populates self.redfish with some hardcoded EventService
            values and values from redfish.conf.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["@odata.context"] = "/redfish/v1/$metadata" \
            "#EventService.EventService"
        self.redfish["@odata.id"] = self.BASE_URI

        self.redfish["Id"] = "EventService"
        self.redfish["Name"] = "Event Service"
        self.redfish["Description"] = "Event Subscription service"

        self.redfish["DeliveryRetryAttempts"] = delivery_retry_attempts
        self.redfish["DeliveryRetryIntervalSeconds"] = delivery_retry_interval

        # All information bellow is hard-coded
        # until we decide where to find it
        # self.redfish["Status"] = dict()
        # self.redfish["Status"]["Health"] = "OK"
        # self.redfish["Status"]["HealthRollup"] = "OK"
        # self.redfish["Status"]["State"] = "Enabled"

        # Disable Event Service if authentication mode is conf
        auth_mode = config.get_authentication_mode()
        if auth_mode == "session":
            self.redfish["ServiceEnabled"] = False
        else:
            self.redfish["ServiceEnabled"] = True

            submit_test_event = dict()
            submit_test_event["EventType@Redfish.AllowableValues"] = \
                list(util.get_subscriptions_by_type().keys())
            submit_test_event["target"] = self.BASE_URI + \
                "/Actions/EventService.SubmitTestEvent/"

            self.redfish["Actions"] = dict()
            self.redfish["Actions"]["#EventService.SubmitTestEvent"] = \
                submit_test_event

            self.redfish["Subscriptions"] = dict()
            self.redfish["Subscriptions"]["@odata.id"] = \
                self.BASE_URI + "/EventSubscriptions/"
            self.redfish["EventTypesForSubscription"] = \
                list(util.get_subscriptions_by_type().keys())

        self._validate()
