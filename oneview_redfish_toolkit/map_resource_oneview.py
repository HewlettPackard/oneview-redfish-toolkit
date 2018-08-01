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
import logging
import logging.config

# 3rd party libs
from flask import abort
from flask import g
from flask_api import status
from hpOneView import HPOneViewException
from hpOneView.oneview_client import OneViewClient

# Modules own libs
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit import authentication
from oneview_redfish_toolkit import connection

# Globals vars:
#   globals()['map_resources_ov']

def init_map_resources():
    globals()['map_resources_ov'] = dict()


def get_map_resources():
    return globals()['map_resources_ov']


def query_ov_client_by_resource(resource_id, resource, function,
                                *args, **kwargs):
    ip_oneview = get_ov_ip_by_resource(resource_id)
    
    if not ip_oneview:
        return search_resource_multiple_ov(resource_id, resource, function,
                                *args, **kwargs)

    ov_token = authentication.get_oneview_token(ip_oneview)

    ov_client = connection.get_oneview_client(session_id=ov_token)

    return execute_query_ov_client(ov_client, resource, function,
                                    *args, **kwargs)


def get_ov_ip_by_resource(uuid):
    map_resources = get_map_resources()

    if uuid not in map_resources:
        return None

    ip_oneview = map_resources[uuid]

    return ip_oneview


def search_resource_multiple_ov(resource_id, resource, function,
                                *args, **kwargs):
    ov_ip_tokens = authentication.get_multiple_oneview_token()
    expected_resource = None
    error = None

    for ov_ip, ov_token in ov_ip_tokens.items():
        ov_client = connection.get_oneview_client(session_id=ov_token)

        try:
            result = execute_query_ov_client(ov_client, resource, function,
                                             *args, **kwargs)
        except HPOneViewException as e:
            error = e
    
    if not expected_resource:
        if error and error.oneview_response["errorCode"] == \
            status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise error

        raise OneViewRedfishResourceNotFoundError(
                    resource_id, resource)


def execute_query_ov_client(ov_client, resource, function, *args, **kwargs):
    ov_resource = object.__getattribute__(ov_client, resource)
    ov_function = object.__getattribute__(ov_resource, function)

    return ov_function(*args, **kwargs)


def _get_ov_client_by_resource(resource_id):
    return g.oneview_connection


def _get_all_oneviews_clients():
    return [g.oneview_connection]
