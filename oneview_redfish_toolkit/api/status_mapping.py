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

STATUS_MAP = {
    "OK": {
        "State": "Enabled",
        "Health": "OK"
    },
    "Disabled": {
        "State": "Disabled",
        "Health": "Warning"
    },
    "Warning": {
        "State": "Enabled",
        "Health": "Warning"
    },
    "Critical": {
        "State": "Enabled",
        "Health": "Critical"
    },
    "Unknown": {
        "State": "Absent",
        "Health": None
    }
}


def get_redfish_state(oneview_status):
    """Gets corresponding Redfish State"""

    return STATUS_MAP[oneview_status]["State"]


def get_redfish_health(oneview_status):
    """Gets corresponding Redfish Health"""

    return STATUS_MAP[oneview_status]["Health"]
