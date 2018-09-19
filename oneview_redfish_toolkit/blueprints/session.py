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

# 3rd party libs
from flask import abort
from flask import Blueprint
from flask import request
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.session import Session
from oneview_redfish_toolkit.api.session_collection import SessionCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import client_session

session = Blueprint('session', __name__)


@session.route(SessionCollection.BASE_URI, methods=["GET"])
def get_collection():
    result = SessionCollection(client_session.get_session_ids())
    return ResponseBuilder.success(result)


@session.route(SessionCollection.BASE_URI + "/" + "<session_id>",
               methods=["GET"])
def get_session(session_id):
    if session_id not in client_session.get_session_ids():
        abort(status.HTTP_404_NOT_FOUND)

    return ResponseBuilder.success(Session(session_id))


@session.route(SessionCollection.BASE_URI + "/" + "<session_id>",
               methods=["DELETE"])
def delete_session(session_id):
    token = request.headers.get('x-auth-token')
    session_for_delete = client_session.get_session_id_by_token(token)

    if session_id != session_for_delete:
        abort(status.HTTP_404_NOT_FOUND)

    client_session.clear_session_by_token(token)

    return Response(status=status.HTTP_204_NO_CONTENT,
                    mimetype="application/json")


@session.route(SessionCollection.BASE_URI, methods=["POST"])
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
            return abort(401)

            OneViewRedfishError: When occur a credential key mapping error.
            return abort(400)
    """

    try:
        try:
            body = request.get_json()
            username = body["UserName"]
            password = body["Password"]
        except Exception:
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key. The JSON request body"
                            " must have the keys UserName and Password"})

        token, session_id = client_session.login(username, password)

        sess = Session(session_id)

        return ResponseBuilder.success(sess, {
            "Location": sess.redfish["@odata.id"],
            "X-Auth-Token": token
        })

    except HPOneViewException as e:
        logging.exception('Unauthorized error: {}'.format(e))
        abort(status.HTTP_401_UNAUTHORIZED)
    except OneViewRedfishError as e:
        logging.exception('Mapping error: {}'.format(e))
        abort(status.HTTP_400_BAD_REQUEST, e.msg['message'])
