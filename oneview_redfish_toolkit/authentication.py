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
import logging.config

# 3rd party libs
from flask import abort
from flask_api import status
from hpOneView import HPOneViewException
from hpOneView.oneview_client import OneViewClient

# Modules own libs
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection


# Globals vars:
#   globals()['map_tokens']

def get_map_tokens():
    return globals()['map_tokens']


def login(username, password):
    try:
        tokens_ov_by_ip = dict()
        credentials = create_credentials(username, password)

        for ip in config.get_oneview_multiple_ips():
            ov_config = \
                connection.create_oneview_config(ip=ip,
                                                 credentials=credentials)
            oneview_client = OneViewClient(ov_config)
            token_ov = oneview_client.connection.get_session_id()

            tokens_ov_by_ip[ip] = token_ov

        redfish_token = next(iter(tokens_ov_by_ip.values()))

        if 'map_tokens' not in globals():
            globals()['map_tokens'] = dict()

        globals()['map_tokens'][redfish_token] = tokens_ov_by_ip

        return redfish_token
    except HPOneViewException as e:
        logging.exception('Unauthorized error: {}'.format(e))
        raise e


def check_authentication(rf_token):
    if rf_token not in get_map_tokens():
        msg = 'Unauthorized error for redfish token: {}'.format(rf_token)
        logging.exception(msg)
        abort(status.HTTP_401_UNAUTHORIZED, msg)


def get_oneview_token(rf_token, ip_oneview):
    try:
        return get_map_tokens()[rf_token][ip_oneview]
    except KeyError:
        msg = 'Unauthorized error for redfish token {} and OneView IP {}' \
            .format(rf_token, ip_oneview)
        logging.exception(msg)
        abort(status.HTTP_401_UNAUTHORIZED, msg)


def create_credentials(username, password):
    credentials = dict()
    credentials["userName"] = username
    credentials["password"] = password
    return credentials
