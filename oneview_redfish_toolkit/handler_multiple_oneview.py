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

# Modules own libs
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import all_oneviews_resource
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import filter_uuid_parameter_resource
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import first_parameter_resource
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import second_parameter_resource
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import spt_get_all_with_filter


RESOURCE_STRATEGY = {
    # Check if is query on all OneViews
    "appliance_node_information": {"get_version": all_oneviews_resource},
    "connection": {"get": first_parameter_resource},
    "drive_enclosures": {"get": first_parameter_resource},
    "enclosures": {
        "get": first_parameter_resource,
        "get_all": all_oneviews_resource,
        "get_environmental_configuration": first_parameter_resource,
        "get_utilization": first_parameter_resource,
        },
    "ethernet_networks": {"get": first_parameter_resource},
    "index_resources": {
        "get": first_parameter_resource,
        "get_all": filter_uuid_parameter_resource,
        },
    "logical_enclosures": {"get": first_parameter_resource},
    "network_sets": {"get": first_parameter_resource},
    "racks": {
        "get": first_parameter_resource,
        "get_all": all_oneviews_resource,
        "get_device_topology": first_parameter_resource,
        },
    "sas_logical_jbods": {
        "get": first_parameter_resource,
        "get_drives": first_parameter_resource,
        },
    "server_hardware": {
        "get": first_parameter_resource,
        "get_all": all_oneviews_resource,
        "get_utilization": first_parameter_resource,
        "update_power_state": second_parameter_resource,
        },
    "server_hardware_types": {"get": first_parameter_resource},
    "server_profiles": {
        "delete": first_parameter_resource,
        "get": first_parameter_resource,
        "get_available_targets": first_parameter_resource,
        },
    "server_profile_templates": {
        "get": first_parameter_resource,
        "get_all": spt_get_all_with_filter,
        },
}


class MultipleOneViewResource(object):

    def __getattribute__(self, name):
        return MultipleOneViewResourceFunction(name)


class MultipleOneViewResourceFunction(object):
    def __init__(self, resource_name):
        self.multiple_ov_resource_name = resource_name

    def __getattribute__(self, name):
        if name == 'multiple_ov_resource_name':
            return object.__getattribute__(self, name)

        return MultipleOneViewResourceRetriever(
            self.multiple_ov_resource_name, name).retrieve


class MultipleOneViewResourceRetriever(object):

    def __init__(self, resource_name, function_name):
        self.multiple_ov_resource_name = resource_name
        self.multiple_ov_function_name = function_name

    def retrieve(self, *args, **kwargs):
        resource = self.multiple_ov_resource_name
        function = self.multiple_ov_function_name

        get_ov_client_strategy = RESOURCE_STRATEGY[resource][function]
        result = get_ov_client_strategy(resource, function, *args, **kwargs)

        return result
