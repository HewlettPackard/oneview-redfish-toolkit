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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class SubscriptionCollection(RedfishJsonValidator):
    """Creates a Subscription Collection Redfish dict

        Populates self.redfish with some hardcoded SubscriptionCollection
        values
    """

    SCHEMA_NAME = 'EventDestinationCollection'

    def __init__(self, all_subscriptions):
        """SubscriptionCollection constructor.

            Populates self.redfish with hardcoded SubscriptionCollection
            values.

            all_subscriptions: Dictionary with all subscriptions.
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Name"] = "Event Subscriptions Collection"
        self.redfish["Members@odata.count"] = len(all_subscriptions)
        self.redfish["Members"] = list()

        for subscription_id in all_subscriptions:
            member = collections.OrderedDict()
            member["@odata.id"] = \
                "/redfish/v1/EventService" \
                "/EventSubscriptions/{}".format(
                    all_subscriptions[subscription_id].get_id())

            self.redfish["Members"].append(member)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EventDestinationCollection" \
            ".EventDestinationCollection"
        self.redfish["@odata.id"] = \
            "/redfish/v1/EventService/EventSubscriptions/"

        self._validate()
