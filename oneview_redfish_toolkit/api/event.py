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

import os

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


ONEVIEW_TO_REDFISH_EVENTS = {
    "Created": "ResourceAdded",
    "Updated": "ResourceUpdated",
    "Deleted": "ResourceRemoved",

    # OneView does not have an equivalent change type to StatusChange
    "StatusChange": "StatusChange"
}


class Event(RedfishJsonValidator):
    """Creates a Event Redfish dict

        Populates self.redfish with some hardcoded Event
        values and with the SCMB message received from OneView.
    """

    SCHEMA_NAME = 'Event'

    def __init__(self, oneview_message):
        """Event constructor

        Populates self.redfish with some hardcoded Event
        values and with the SCMB message received from OneView.

            Args:
                oneview_message: A dict with an OneView SCMB message
        """

        super().__init__(self.SCHEMA_NAME)

        category = oneview_message["resource"]["category"]

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["@odata.context"] = "/redfish/v1/$metadata#Event.Event"
        self.redfish["Events@odata.count"] = 1
        self.redfish["Events"] = list()

        if (category == "alerts"):
            self.build_event_from_alert(oneview_message)
        else:
            self.build_event_from_task(oneview_message)

        self._validate()

    def build_event_from_alert(self, oneview_alert):
        associated_resource = oneview_alert["resource"]["associatedResource"]
        event_id = str(os.path.basename(associated_resource["resourceUri"]))

        self.redfish["Id"] = event_id
        self.redfish["Name"] = associated_resource["resourceName"]

        event_record = {}
        event_record["EventTimestamp"] = oneview_alert["timestamp"]
        event_record["EventType"] = "Alert"
        event_record["MessageId"] = "Base.1.1.Success"
        # TODO(svoboda) add link to Redfish resource
        # event_record["OriginOfCondition"] = origin_of_condition

        self.redfish["Events"].append(event_record)

    def build_event_from_task(self, oneview_task):
        event_id = str(os.path.basename(oneview_task["resourceUri"]))

        self.redfish["Id"] = event_id
        self.redfish["Name"] = oneview_task["resource"]["name"]

        event_record = {}
        event_record["EventTimestamp"] = oneview_task["timestamp"]
        event_record["EventType"] = \
            ONEVIEW_TO_REDFISH_EVENTS[oneview_task["changeType"]]
        event_record["MessageId"] = "Base.1.1.Success"
        # TODO(svoboda) add link to Redfish resource
        # event_record["OriginOfCondition"] = origin_of_condition

        self.redfish["Events"].append(event_record)
