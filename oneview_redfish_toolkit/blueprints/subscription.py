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

import logging
import uuid

from flask import abort
from flask import Blueprint
from flask import request
from flask import Response
from flask_api import status
from jsonschema.exceptions import ValidationError
import validators

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.subscription import Subscription
from oneview_redfish_toolkit import util


subscription = Blueprint("subscription", __name__)


@subscription.route(
    "/redfish/v1/EventService/EventSubscriptions/", methods=["POST"])
def add_subscription():
    """Add the Redfish Subscription.

        Add a new subscription when this POST operation is requested.
        The body of the request must have the Destination,
        an array of EventTypes. Context is optional.

        EventTypes:
            - ResourceUpdated
            - ResourceAdded
            - ResourceRemoved
            - Alert

        Returns:
            JSON: JSON with Subscription information.

        Exception:
            OneViewRedfishError: When occur a key mapping error.
            return abort(400)

            Exception: Unexpected error.
            return abort(500)
    """
    try:
        # get Destination, EventTypes and Context from post
        # generate subscription uuid
        # add subscription in subscriptions_by_type
        # add subscription in all_subscriptions

        try:
            body = request.get_json()
            destination = body["Destination"]

            if not validators.url(destination):
                raise OneViewRedfishError(
                    {"errorCode": "INVALID_INFORMATION",
                     "message": "Destination must be an URI."})

            event_types = body["EventTypes"]

            if not event_types:
                raise OneViewRedfishError(
                    {"errorCode": "INVALID_INFORMATION",
                     "message": "EventTypes cannot be empty."})

            context = body.get("Context")
        except KeyError:
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key. The JSON request body"
                            " must have the keys Destination and EventTypes."
                            " The Context is optional."})

        subscription_id = str(uuid.uuid1())

        try:
            # Build Subscription object and validates it
            sc = Subscription(subscription_id, destination,
                              event_types, context)
        except ValidationError:
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid EventType. The EventTypes are "
                            "StatusChange, ResourceUpdated, ResourceAdded,"
                            " ResourceRemoved and Alert."})

        for event_type in sc.get_event_types():
            util.get_subscriptions_by_type()[event_type][subscription_id] = sc

        util.get_all_subscriptions()[subscription_id] = sc

        # Build redfish json
        json_str = sc.serialize()

        # Build response and returns
        response = Response(
            response=json_str,
            status=status.HTTP_201_CREATED,
            mimetype="application/json")
        response.headers.add(
            "Location", "/redfish/v1/EventService/EventSubscriptions/"
                        "{}".format(subscription_id))
        return response

    except OneViewRedfishError as e:
        logging.exception(e)
        abort(status.HTTP_400_BAD_REQUEST, e.msg['message'])
    except Exception as e:
        logging.exception(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@subscription.route(
    "/redfish/v1/EventService/EventSubscriptions/<subscription_id>",
    methods=["DELETE"])
def remove_subscription(subscription_id):
    """Removes a specific Subscription

        Args:
            subscription_id: The Subscription ID.
    """
    try:
        sc = util.get_all_subscriptions()[subscription_id]
        event_types = sc.get_event_types()

        for event in event_types:
            del util.get_subscriptions_by_type()[event][subscription_id]

        del util.get_all_subscriptions()[subscription_id]

        return Response(
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except KeyError as e:
        logging.exception("Subscription not found: " + str(e))
        abort(status.HTTP_404_NOT_FOUND)


@subscription.route(
    "/redfish/v1/EventService/EventSubscriptions/<subscription_id>",
    methods=["GET"])
def get_subscription(subscription_id):
    """Gets a specific Subscription

        Args:
            subscription_id: The Subscription ID.

        Returns:
            Subscription JSON.
    """
    try:
        sc = util.get_all_subscriptions()[subscription_id]

        json_str = sc.serialize()
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except KeyError as e:
        logging.exception("Subscription not found: " + str(e))
        abort(status.HTTP_404_NOT_FOUND)
