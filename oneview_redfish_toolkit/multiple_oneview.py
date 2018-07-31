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
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import first_parameter_resource
from oneview_redfish_toolkit.strategy_multiple_oneview \
    import all_oneviews_resource
from oneview_redfish_toolkit import connection


RESOURCE_STRATEGY = {
    "server_hardware": {
        "get": first_parameter_resource,
        "get_all": all_oneviews_resource,
        },
    "server_hardware_types": {"get": first_parameter_resource},
    "server_profiles": {"get": first_parameter_resource},
    "server_profile_templates": {
        "get": first_parameter_resource,
        "get_all": all_oneviews_resource
        },
    "sas_logical_jbods": {"get_drives": first_parameter_resource},
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
