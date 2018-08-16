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

from collections import OrderedDict

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Subscription(RedfishJsonValidator):
    """Creates the Subscription class

        Populates self.redfish with Subscription response.
    """

    SCHEMA_NAME = 'EventDestination'

    def __init__(self, subscription_id, destination, event_types, context):
        """Session constructor

            Populates self.redfish with Subscription response.

            Args:
                subscription_id: Uniquely identifies the resource within
                the collection of like resources.

                destination: The URI of the destination Event Service.

                event_types: This property shall contain the types of events
                that shall be sent to the destination.

                context: A client-supplied string that is stored with the
                event destination subscription.
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = subscription_id
        self.redfish["Name"] = "EventSubscription " + subscription_id
        self.redfish["Destination"] = destination
        self.redfish["EventTypes"] = self. \
            _remove_duplicated_event_types(event_types)
        self.redfish["Context"] = context
        self.redfish["Protocol"] = "Redfish"
        self.redfish["SubscriptionType"] = "RedfishEvent"
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EventDestination.EventDestination"
        self.redfish["@odata.id"] = \
            "/redfish/v1/EventService/EventSubscriptions/" + subscription_id

        self._validate()

    def get_id(self):
        """Gets subscription Id"""
        return self.redfish["Id"]

    def get_event_types(self):
        """Gets the list of event types"""
        return self.redfish["EventTypes"]

    def _remove_duplicated_event_types(self, event_types):
        """Duplicated elements in event_types must be removed.

            OrderedDict keeps the order of the elements,
            so it will preserve list definition.
        """
        # One of the fastest and shortest ways to remove
        # duplicates and keeps the order in Python 3.5
        return list(OrderedDict.fromkeys(event_types))
