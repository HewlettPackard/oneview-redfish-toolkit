# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
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

# 3rd party libs
from flask import abort
from flask import Blueprint
from flask import request
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient

# own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.session import Session
from oneview_redfish_toolkit import util


session = Blueprint('session', __name__)


@session.route('/redfish/v1/SessionService/Sessions', methods=["POST"])
def post_session():
    """Posts Session

        The response to the POST request to create a session includes:

            - An X-Auth-Token header that contains a session auth token that
            the client can use an subsequent requests.
            - A Location header that contains a link to the newly created
            session resource.
            - The JSON response body that contains a full representation of
            the newly created session object.

        Exception:
            HPOneViewException: Invalid username or password.
            return abort(400)

            OneViewRedfishError: When occur a credential key mapping error.
            return abort(400)

            Exception: Unexpected error.
            return abort(500)
    """

    try:
        try:
            body = request.get_json()
            username = body["UserName"]
            password = body["Password"]
        except Exception:
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key"})

        config = dict()
        config["ip"] = util.ov_config["ip"]
        config["credentials"] = dict()
        config["credentials"]["userName"] = username
        config["credentials"]["password"] = password

        oneview_client = OneViewClient(config)
        session_id = oneview_client.connection.get_session_id()

        sess = Session(username)

        json_str = sess.serialize()

        response = Response(
            response=json_str,
            status=200,
            mimetype='application/json')
        response.headers.add(
            "Location", "/redfish/v1/SessionService/Sessions/1")
        response.headers.add("X-Auth-Token", session_id)

        return response

    except HPOneViewException as e:
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_400_BAD_REQUEST)
    except OneViewRedfishError as e:
        logging.exception('Mapping error: {}'.format(e))
        abort(status.HTTP_400_BAD_REQUEST, e.msg['message'])
    except Exception as e:
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
