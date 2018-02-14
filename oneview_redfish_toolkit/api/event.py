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

import os

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Event(RedfishJsonValidator):
    """Creates a Event Redfish dict

        Populates self.redfish with some hardcoded Event
        values and with the response from OneView.
    """

    SCHEMA_NAME = 'Event'

    def __init__(self, oneview_alert, event_type):
        """Event constructor

            Populates self.redfish with some hardcoded Event
            values and with the response from OneView.

            Args:
                oneview_alert: A dict with an OneView alert message
                event_type: string with redfish event_type
        """

        super().__init__(self.SCHEMA_NAME)

        id = str(os.path.basename(oneview_alert["resourceUri"]))

        self.redfish["@odata.type"] = "#Event.v1_2_0.Event"
        self.redfish["Id"] = id
        self.redfish["Name"] = oneview_alert["resource"]["description"]
        self.redfish["Events"] = []
        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Event.Event"
        event_id = 0
        event = {}
        event["EventId"] = str(event_id)
        event["EventType"] = event_type
        # Nothing good matches here!!!!!
        event["MessageId"] = "Base.1.1.Success"
        event["Severity"] = oneview_alert["resource"]["severity"]
        event["EventTimestamp"] = oneview_alert["resource"]["created"]
        self.redfish["Events"].append(event)
        self._validate()
