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

from copy import deepcopy
from flask import abort
from flask import Blueprint
from flask import request
from flask_api import status

from oneview_redfish_toolkit.api.event import Event
from oneview_redfish_toolkit.api.event_service import EventService
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import util

event_service = Blueprint("event_service", __name__)

ONEVIEW_TEST_ALERT = {
    "timestamp": "2018-02-12T20:12:03.231Z",
    "resource": {
        "category": "alerts",
        "associatedResource": {
            "resourceName": "0000A66101, bay 3",
            "resourceUri": "/rest/server-hardware/"
                           "30373737-3237-4D32-3230-313530314752"
        }
    }
}

ONEVIEW_TEST_TASK = {
    "timestamp": "2018-02-12T20:12:03.231Z",
    "resourceUri": "/rest/server-hardware/"
                   "30373737-3237-4D32-3230-313530314752",
    "changeType": None,
    "resource": {
        "category": "server-hardware",
        "name": "0000A66101, bay 3"
    }
}

REDFISH_TO_ONEVIEW_EVENTS = {
    "ResourceAdded": "Created",
    "ResourceUpdated": "Updated",
    "ResourceRemoved": "Deleted"
}


@event_service.route("/redfish/v1/EventService/", methods=["GET"])
def get_event_service():
    """Get the Redfish Event Service.

        Get method to return EventService JSON when
        /redfish/v1/EventService is requested.

        Returns:
            JSON: JSON with EventService.

        Exceptions:
            OneViewRedfishError: General error.
    """
    evs = EventService(util.get_delivery_retry_attempts(),
                       util.get_delivery_retry_interval())

    return ResponseBuilder.success(evs)


@event_service.route(
    "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent/",
    methods=["POST"])
def execute_test_event_action():
    """Executes the SubmitTestEvent Action

        Return a JSON containing the EventType received.
        Logs exception of any error and return abort.

        Returns:
            JSON: JSON containing the EventType.

        Exceptions:
            OneViewRedfishError: When an invalid JSON is received.
            return abort(400)

            Exception: Unexpected error.
            return abort(500)
    """

    if not config.auth_mode_is_conf():
        abort(status.HTTP_404_NOT_FOUND,
              "EventService is not enabled.")

    event_type = None
    try:
        event_type = request.get_json()['EventType']
    except Exception:
        abort(status.HTTP_400_BAD_REQUEST,
              'Invalid JSON data. Missing EventType property.')

    if event_type not in util.get_subscriptions_by_type().keys():
        abort(status.HTTP_400_BAD_REQUEST,
              'Invalid EventType value: %s' % event_type)

    # Creates a sample OneView SCMB message according to
    # the value of 'event_type'
    if event_type == "Alert":
        message = deepcopy(ONEVIEW_TEST_ALERT)
    else:
        message = deepcopy(ONEVIEW_TEST_TASK)
        message['changeType'] = REDFISH_TO_ONEVIEW_EVENTS[event_type]

    event = Event(message)

    util.dispatch_event(event)

    return ResponseBuilder.response(event, status.HTTP_202_ACCEPTED)
