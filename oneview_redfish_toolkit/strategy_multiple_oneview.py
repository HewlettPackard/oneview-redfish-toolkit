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
from oneview_redfish_toolkit import multiple_oneview


def first_parameter_resource(resource, function, *args, **kwargs):
    resource_id = args[0]

    return multiple_oneview.query_ov_client_by_resource(resource_id, resource,
                                                        function, *args,
                                                        **kwargs)


def filter_uuid_parameter_resource(resource, function, *args, **kwargs):
    if 'filter' not in kwargs:
        return all_oneviews_resource(resource, function, *args, **kwargs)

    filter_parameter = kwargs['filter']
    resource_id = filter_parameter.split('=')[1]

    return multiple_oneview.query_ov_client_by_resource(resource_id, resource,
                                                        function, *args,
                                                        **kwargs)


def all_oneviews_resource(resource, function, *args, **kwargs):
    all_results = multiple_oneview.search_resource_multiple_ov(resource,
                                                               function, None,
                                                               *args,
                                                               **kwargs)

    return all_results


def spt_get_all_with_filter(resource, function, *args, **kwargs):
    if 'filter' not in kwargs:
        return all_oneviews_resource(resource, function, *args, **kwargs)

    filter_parameter = kwargs['filter']

    for filters in filter_parameter:
        filter_data = filters.split('=')
        if filter_data[0] == 'enclosureGroupUri':
            resource_id = filter_data[1]
            return \
                multiple_oneview.query_ov_client_by_resource(resource_id,
                                                             resource,
                                                             function,
                                                             *args, **kwargs)


def create_server_profile(resource, function, *args, **kwargs):
    sp = args[0]
    spt_uuid = sp['description']
    return _run_action(spt_uuid, 'server_profile_templates', 'get', resource,
                       function, *args, **kwargs)


def delete_server_profile(resource, function, *args, **kwargs):
    sp_uuid = args[0]
    return _run_action(sp_uuid, 'server_profiles', 'get', resource,
                       function, *args, **kwargs)


def update_power_state_server_hardware(resource, function, *args, **kwargs):
    sh_uuid = args[1]
    return _run_action(sh_uuid, 'server_hardware', 'get', resource,
                       function, *args, **kwargs)


def _run_action(resource_id, resource_get, function_get, resource,
                function, *args, **kwargs):

    # Check if the resource_id is already mapped
    if not multiple_oneview.get_ov_ip_by_resource(resource_id):
        # Mapping OneView for the resource_id
        multiple_oneview.query_ov_client_by_resource(resource_id,
                                                     resource_get,
                                                     function_get,
                                                     resource_id, **{})

    # Running action on OneView already mapped for resource_id
    return multiple_oneview.query_ov_client_by_resource(resource_id,
                                                        resource, function,
                                                        *args, **kwargs)
