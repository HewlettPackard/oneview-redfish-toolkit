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

# Python libs
import collections

# Modules own libs
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
import oneview_redfish_toolkit.api.status_mapping as status_mapping


class Manager(RedfishJsonValidator):
    """Creates a Manager Redfish dict

        Populates self.redfish with some hardcoded Manager
        values and with the response from OneView.
    """

    SCHEMA_NAME = 'Manager'

    def __init__(self, oneview_appliance_info, oneview_appliance_state,
                 oneview_appliance_health_status):
        """Manager constructor

            Populates self.redfish with some hardcoded Manager
            values and with the response from OneView.

            Args:
                oneview_appliance_info: An Oneview's appliance info dict
                oneview_appliance_state: An Oneview's appliance status dict
                oneview_appliance_health_status: An Oneview's appliance
                health state dict
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = oneview_appliance_info['uuid']
        self.redfish["Description"] = oneview_appliance_info["family"]
        self.redfish["ManagerType"] = "Service"
        self.redfish["FirmwareVersion"] = \
            oneview_appliance_info["softwareVersion"]
        self.redfish["Status"] = collections.OrderedDict()
        state = status_mapping.APPLIANCE_STATE_TO_REDFISH_STATE.\
            get(oneview_appliance_state["state"])
        health = self._get_highest_health_state(
            oneview_appliance_health_status["members"])
        self.redfish["Status"]["State"] = state
        self.redfish["Status"]["Health"] = health
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Manager.Manager"
        self.redfish["@odata.id"] = \
            "/redfish/v1/Managers/" + oneview_appliance_info['uuid']

    @staticmethod
    def _get_highest_health_state(health_state_members):
        health_state_result = None
        highest_status = 0

        for member in health_state_members:
            redfish_health_state = status_mapping.MANAGER_HEALTH_STATE. \
                get(member["severity"])
            current_status = \
                status_mapping.CRITICALITY_STATUS[redfish_health_state]

            if current_status > highest_status:
                highest_status = current_status
                health_state_result = redfish_health_state

        return health_state_result
