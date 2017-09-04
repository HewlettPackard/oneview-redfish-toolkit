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
from oneview_redfish_toolkit.api.manager \
    import Manager


class EnclosureManager(Manager):
    """Creates a Manager Redfish dict for Enclosure

        Populates self.redfish with some hardcoded Manager
        values and with the response from OneView.
    """

    def __init__(self, enclosure, oneview_version):
        """EnclosureManager constructor

            Populates self.redfish with some hardcoded Manager
            values and with the response from OneView.

            Args:
                enclosure: A dict for an enclosure
                oneview_version: OneView version string
        """

        super().__init__(enclosure, oneview_version)

        self.redfish["ManagerType"] = "EnclosureManager"
        self.redfish["Name"] = "Enclosure Manager"
        self.redfish["Description"] = "HPE OneView Manager"
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["Links"]["ManagerForChassis"] = list()
        self.redfish["Links"]["ManagerForChassis"].append(
            {"@odata.id": "/redfish/v1/Chassis/" + enclosure['uuid']}
        )

        self._validate()
