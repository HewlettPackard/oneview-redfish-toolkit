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
from flask_api import status
from hpOneView.oneview_client import OneViewClient
from http.client import HTTPSConnection

# Modules own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import config


# Globals vars:
#   globals()['ov_client']


def get_oneview_client(session_id=None, is_service_root=False,
                       api_version=None):
    """Establishes a OneView connection to be used in the module

        Establishes a OV connection if one does not exists.
        If one exists, do a single OV access to check if its sill
        valid. If not tries to establish a new connection.
        Sets the connection on the ov_conn global var

        Args:
            session_id: The ID of a valid authenticated session, if the
            authentication_mode is session. Defaults to None.

            is_service_root: Informs if who is calling this function is the
            ServiceRoot blueprint. If true, even if authentication_mode is
            set to session it will use the information on the conf file to
            return a connection.  This is a workaround to allow ServiceRoot
            to retrieve the appliance UUID before user logs in.

        Returns:
            OneViewClient object

        Exceptions:
            HPOneViewException if can't connect or reconnect to OV
    """

    auth_mode = config.get_authentication_mode()

    if auth_mode == "conf" or is_service_root:
        # Doing conf based authentication
        ov_config = create_oneview_config(ip=config.get_oneview_ip(),
                                          credentials=config.get_credentials())
        ov_client = None

        # Check if connection is ok yet
        try:
            # Check if OneViewClient already exists
            if 'ov_client' not in globals():
                globals()['ov_client'] = OneViewClient(ov_config)

            ov_client = globals()['ov_client']
            ov_client.connection.get('/rest/logindomains')
            return ov_client
        # If expired try to make a new connection
        except Exception:
            try:
                logging.exception('Re-authenticated')
                if ov_client:
                    ov_client.connection.login(config.get_credentials())
                    return ov_client
            # if failed abort
            except Exception:
                raise
    else:
        # Auth mode is session
        ov_config = create_oneview_config(ip=config.get_oneview_ip(),
                                          session_token=session_id)
        try:
            oneview_client = OneViewClient(ov_config)
            oneview_client.connection.get('/rest/logindomains')
            return oneview_client
        except Exception:
            logging.exception("Failed to recover session based connection")
            raise


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


def create_oneview_config(ip, session_token=None, api_version=None,
                          credentials=None):
    """Creates a dict to pass as argument on creating a new OneViewClient"""
    ov_config = {}
    ov_config['ip'] = ip
    ov_config['api_version'] = config.get_api_version()

    if session_token:
        ov_config['credentials'] = {"sessionID": session_token}

    if credentials:
        ov_config['credentials'] = credentials

    if api_version:
        ov_config['api_version'] = api_version

    return ov_config
