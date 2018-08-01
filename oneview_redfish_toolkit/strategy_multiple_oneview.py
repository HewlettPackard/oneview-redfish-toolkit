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
from hpOneView import HPOneViewException
from hpOneView.oneview_client import OneViewClient

# Modules own libs
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit.map_resource_oneview \
    import query_ov_client_by_resource
from oneview_redfish_toolkit.map_resource_oneview \
    import execute_query_ov_client
from oneview_redfish_toolkit.map_resource_oneview \
    import get_all_oneviews_clients

def first_parameter_resource(resource, function, *args, **kwargs):
    resource_id = args[0]

    return query_ov_client_by_resource(resource_id, resource, function,
                                       *args, **kwargs)


def all_oneviews_resource(resource, function, *args, **kwargs):
    all_ov_clients = get_all_oneviews_clients()
    all_results = []

    for ov_client in all_ov_clients:
        result = execute_query_ov_client(ov_client, resource, function,
                                          *args, **kwargs)
        result.append(result)

    return all_results