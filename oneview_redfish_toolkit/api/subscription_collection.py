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

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit import util


class SubscriptionCollection(RedfishJsonValidator):
    """Creates a Subscription Collection Redfish dict

        Populates self.redfish with some hardcoded SubscriptionCollection
        values
    """

    SCHEMA_NAME = 'EventDestinationCollection'

    def __init__(self):
        """SubscriptionCollection constructor.

            Populates self.redfish with hardcoded SubscriptionCollection
            values.
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = \
            "#EventDestinationCollection.EventDestinationCollection"
        self.redfish["Name"] = "Event Subscriptions Collection"
        self.redfish["Members@odata.count"] = len(util.all_subscriptions)
        self.redfish["Members"] = list()
        self.redfish["Members"].append(collections.OrderedDict())

        for subscription in util.all_subscriptions:
            member = collections.OrderedDict()
            member["@odata.id"] = \
                "/redfish/v1/EventService" \
                "/Subscriptions/{}".format(subscription.redfish["Id"])

            self.redfish["Members"].append(member)

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#EventDestinationCollection" \
            ".EventDestinationCollection"
        self.redfish["@odata.id"] = \
            "/redfish/v1/EventService/EventSubscriptions/"

        self._validate()
