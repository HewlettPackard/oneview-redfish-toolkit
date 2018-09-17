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
from threading import Lock

# 3rd party libs
from flask import abort
from flask import request
from flask_api import status
from hpOneView import HPOneViewException

# Modules own libs
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import multiple_oneview


# Globals vars:
#   globals()['map_clients']


def _get_map_clients():
    return globals()['map_clients']


def init_map_clients():
    globals()['map_clients'] = dict()


def _set_new_client_by_token(redfish_token, client_ov_by_ip):
    lock = Lock()
    with lock:
        globals()['map_clients'][redfish_token] = client_ov_by_ip


def _set_new_clients_by_ip(ov_clients_by_ip):
    lock = Lock()
    with lock:
        globals()['map_clients'] = ov_clients_by_ip


def login(username, password):
    try:
        clients_ov_by_ip = dict()
        tokens = []

        for ip in config.get_oneview_multiple_ips():
            oneview_client = connection.new_oneview_client(ip, username,
                                                           password)
            tokens.append(oneview_client.connection.get_session_id())

            clients_ov_by_ip[ip] = oneview_client
            _set_manager_into_resource_map(ip, oneview_client)

        redfish_token = tokens[0]

        _set_new_client_by_token(redfish_token, clients_ov_by_ip)

        return redfish_token
    except HPOneViewException as e:
        logging.exception('Unauthorized error: {}'.format(e))
        raise e


def login_conf_mode():
    try:
        clients_ov_by_ip = dict()

        for ip in config.get_oneview_multiple_ips():
            oneview_client = connection.new_oneview_client(ip)
            clients_ov_by_ip[ip] = oneview_client

            _set_manager_into_resource_map(ip, oneview_client)

        _set_new_clients_by_ip(clients_ov_by_ip)
    except HPOneViewException as e:
        logging.exception('Unauthorized error: {}'.format(e))
        raise e


def check_authentication(rf_token):
    if rf_token not in _get_map_clients():
        msg = 'Unauthorized error for redfish token: {}'.format(rf_token)
        logging.exception(msg)
        abort(status.HTTP_401_UNAUTHORIZED, msg)


def _get_oneview_client_by_token(ip_oneview):
    try:
        rf_token = request.headers.get('x-auth-token')
        oneview_client = _get_map_clients()[rf_token][ip_oneview]
        return oneview_client
    except KeyError:
        msg = 'Unauthorized error for redfish token {}' \
            .format(rf_token)
        logging.exception(msg)
        abort(status.HTTP_401_UNAUTHORIZED, msg)


def _get_oneview_client_by_ip(ip_oneview):
    oneview_client = _get_map_clients()[ip_oneview]
    return oneview_client


def get_oneview_client(ip_oneview):
    if config.auth_mode_is_session():
        return _get_oneview_client_by_token(ip_oneview)

    if config.auth_mode_is_conf():
        return _get_oneview_client_by_ip(ip_oneview)


def _set_manager_into_resource_map(ip, oneview_client):
    manager = oneview_client.appliance_node_information.get_version()
    multiple_oneview.set_map_resources_entry(manager["uuid"], ip)
