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

# Python libs
import logging

# Modules own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import strategy_multiple_oneview as st


RESOURCE_STRATEGY = {
    "appliance_node_information": {
        "get_version": st.all_oneviews_resource,
        "get_status": st.all_oneviews_resource
    },
    "connection": {
        "get": st.first_parameter_resource,
        "post": st.create_server_profile,
        },
    "drive_enclosures": {
        "get": st.first_parameter_resource,
        "get_all": st.drive_enclosures_get_all_with_filter,
    },
    "enclosures": {
        "get": st.first_parameter_resource,
        "get_all": st.all_oneviews_resource,
        "get_environmental_configuration": st.first_parameter_resource,
        "get_utilization": st.first_parameter_resource,
        },
    "ethernet_networks": {"get": st.first_parameter_resource},
    "index_resources": {
        "get": st.first_parameter_resource,
        "get_all": st.filter_uuid_parameter_resource,
        },
    "logical_enclosures": {
        "get": st.first_parameter_resource,
        "get_all": st.all_oneviews_resource,
        },
    "network_sets": {"get": st.first_parameter_resource},
    "racks": {
        "get": st.first_parameter_resource,
        "get_all": st.all_oneviews_resource,
        "get_device_topology": st.first_parameter_resource,
        },
    "sas_logical_jbods": {
        "get": st.first_parameter_resource,
        "get_drives": st.first_parameter_resource,
        },
    "server_hardware": {
        "get": st.first_parameter_resource,
        "get_all": st.all_oneviews_resource,
        "get_utilization": st.first_parameter_resource,
        "update_power_state": st.update_power_state_server_hardware,
        },
    "server_hardware_types": {"get": st.first_parameter_resource},
    "server_profiles": {
        "delete": st.delete_server_profile,
        "get": st.first_parameter_resource,
        "get_available_targets": st.first_parameter_resource,
        },
    "server_profile_templates": {
        "get": st.first_parameter_resource,
        "get_all": st.spt_get_all_with_filter,
        },
    "tasks": {
        "get": st.first_parameter_resource
        },
    "labels": {
        "create": st.create_labels,
        "get_by_resource": st.first_parameter_resource
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

        try:
            get_ov_client_strategy = RESOURCE_STRATEGY[resource][function]
        except KeyError as e:
            msg = 'Not mapped strategy on multiple OneViews' \
                  'support for method {}.{} : {}'. \
                  format(resource, function, e)
            logging.exception(msg)
            raise OneViewRedfishError(msg)
        result = get_ov_client_strategy(resource, function, *args, **kwargs)

        return result
