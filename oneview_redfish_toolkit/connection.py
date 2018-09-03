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
import json
import logging
import logging.config
import ssl
import time

# 3rd party libs
from flask import request
from flask_api import status
from hpOneView.oneview_client import OneViewClient
from http.client import HTTPSConnection

# Modules own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import config


SERVICE_ROOT_ENDPOINTS = ["/redfish/v1",
                          "/redfish",
                          "/redfish/v1/odata",
                          "/redfish/v1/$metadata"]


def new_oneview_client(ip_oneview, username=None, password=None,
                       api_version=None):
    credentials = None

    if config.auth_mode_is_conf():
        credentials = config.get_credentials()

    if config.auth_mode_is_session():
        credentials = create_credentials(username, password)

    ov_config = create_oneview_config(ip=ip_oneview,
                                      api_version=api_version,
                                      credentials=credentials)
    try:
        oneview_client = OneViewClient(ov_config)
        return oneview_client
    except Exception:
        logging.exception("Failed to recover session based connection")
        raise


def is_service_root():
    if request.path.rstrip("/") in SERVICE_ROOT_ENDPOINTS:
        return True

    return False


def check_oneview_availability(oneview_ip):
    """Check OneView availability by doing a GET request to OneView"""
    attempts = 3
    retry_interval_sec = 3

    for attempt_counter in range(attempts):
        try:
            status_ov = request_oneview(oneview_ip, '/controller-state.json')

            if status_ov['state'] != 'OK':
                message = "OneView state is not OK at {}".format(
                    oneview_ip)
                raise OneViewRedfishError(message)

            return
        except Exception as e:
            logging.exception(
                'Attempt {} to check OneView availability. '
                'Error: {}'.format(attempt_counter + 1, e))

            if attempt_counter + 1 < attempts:
                time.sleep(retry_interval_sec)

    message = "After {} attempts OneView is unreachable at {}".format(
        attempts, oneview_ip)
    raise OneViewRedfishError(message)


def request_oneview(oneview_ip, rest_url):
    try:
        connection = HTTPSConnection(
            oneview_ip, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))

        connection.request(
            method='GET', url=rest_url,
            headers={'Content-Type': 'application/json',
                     'X-API-Version': config.get_api_version()}
            )

        response = connection.getresponse()

        if response.status != status.HTTP_200_OK:
            message = "OneView is unreachable at {}".format(
                oneview_ip)
            raise OneViewRedfishError(message)

        text_response = response.read().decode('UTF-8')
        json_response = json.loads(text_response)

        return json_response
    finally:
        connection.close()


def create_credentials(username, password):
    credentials = dict()

    try:
        login_domain, username = username.split("\\")
    except (AttributeError, ValueError):
        logging.debug("AuthLoginDomain not specified on session creation")
    else:
        credentials["authLoginDomain"] = login_domain

    credentials["userName"] = username
    credentials["password"] = password
    return credentials


def create_oneview_config(ip, api_version=None, credentials=None):
    """Creates a dict to pass as argument on creating a new OneViewClient"""
    ov_config = {}
    ov_config['ip'] = ip
    ov_config['api_version'] = config.get_api_version()

    if credentials:
        ov_config['credentials'] = credentials

    if api_version:
        ov_config['api_version'] = api_version

    return ov_config
