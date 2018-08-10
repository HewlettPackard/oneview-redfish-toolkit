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


class Manager(RedfishJsonValidator):
    """Creates a Manager Redfish dict

        Populates self.redfish with some hardcoded Manager
        values and with the response from OneView.
    """

    SCHEMA_NAME = 'Manager'

    def __init__(self, oneview_resource, firmware_version):
        """Manager constructor

            Populates self.redfish with some hardcoded Manager
            values and with the response from OneView.

            Args:
                oneview_resource: A dict for ServerHardware or Enclosure
        """

        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = oneview_resource['uuid']
        self.redfish["Description"] = None
        self.redfish["FirmwareVersion"] = firmware_version

        # TODO(victorhugorodrigues): update state and health properties
        # self.redfish["Status"] = collections.OrderedDict()
        # state, _ = status_mapping.\
        #     get_redfish_server_hardware_status_struct(oneview_resource)
        # self.redfish["Status"]["State"] = state
        # self.redfish["Status"]["Health"] = health

        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Manager.Manager"
        self.redfish["@odata.id"] = \
            "/redfish/v1/Managers/" + oneview_resource['uuid']
