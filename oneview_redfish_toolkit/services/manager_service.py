# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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

# Own libs
from oneview_redfish_toolkit import multiple_oneview


def get_manager_uuid(resource_id):
    map_resources = multiple_oneview.get_map_resources()
    ov_ip = map_resources.get(resource_id)

    map_appliances = multiple_oneview.get_map_appliances()
    manager_uuid = map_appliances.get(ov_ip)

    return manager_uuid


def get_oneview_ip_by_manager_uuid(uuid):
    map_appliances = multiple_oneview.get_map_appliances()
    for ov_ip, appliance_uuid in map_appliances.items():
        if appliance_uuid == uuid:
            return ov_ip

    return None
