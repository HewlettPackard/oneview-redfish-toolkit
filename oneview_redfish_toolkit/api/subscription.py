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


class Subscription(RedfishJsonValidator):
    """Creates the Subscription class

        Populates self.redfish with Subscription response.
    """

    SCHEMA_NAME = 'EventDestination'

    def __init__(self, subscription_id, event_types):
        """Session constructor

            Populates self.redfish with Subscription response.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = \
            "#EventDestination.v1_2_0.EventDestination"
        self.redfish["Id"] = subscription_id
        self.redfish["Name"] = "EventSubscription " + subscription_id
        self.redfish["Destination"] = "http://www.dnsname.com/Destination1"
        self.redfish["EventTypes"] = event_types
        self.redfish["Context"] = "WebUser3"
        self.redfish["Protocol"] = "Redfish"
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EventDestination.EventDestination"
        self.redfish["@odata.id"] = "/redfish/v1/EventService/Subscriptions/1"

        self._validate()
