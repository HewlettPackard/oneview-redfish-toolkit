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
from oneview_redfish_toolkit import authentication
from oneview_redfish_toolkit import connection

# Globals vars:
#   globals()['map_resources_ov']

def init_map_resources():
    globals()['map_resources_ov'] = dict()

def get_map_resources():
    return globals()['map_resources_ov']

def get_ov_client_by_resource(uuid):
    map_resources = get_map_resources()

    if uuid not in map_resources:
        return None

    ip_oneview = map_resources[uuid]

    ov_token = authentication.get_oneview_token(ip_oneview)

    return connection.get_oneview_client(session_id=ov_token)

