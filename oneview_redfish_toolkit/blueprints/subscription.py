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

import logging

from flask import abort
from flask import Blueprint
from flask import request
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.subscription import Subscription
from oneview_redfish_toolkit import util


subscription = Blueprint("subscription", __name__)


@subscription.route(
    "/redfish/v1/EventService/EventSubscriptions/", methods=["POST"])
def add_subscription():
    """Add the Redfish Subscription.

        Add a new subscription when this POST operation is requested.
        The body of the request must have an array of EventTypes.

        EventTypes:
            - StatusChange
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
        # get information from post
        # add subscription in subscriptions_by_type
        # add subscription in all_subscriptions
        # the subscription id is len(all_subscriptions) + 1

        try:
            body = request.get_json()
            event_types = body["EventTypes"]
        except Exception:
            raise OneViewRedfishError(
                {"errorCode": "INVALID_INFORMATION",
                 "message": "Invalid JSON key. The JSON request body"
                            " must have the key EventTypes."})

        subscription_id = str(len(util.all_subscriptions) + 1)

        # Build Subscription object and validates it
        sc = Subscription(subscription_id, event_types)

        for event_type in event_types:
            if event_type not in util.subscriptions_by_type:
                util.subscriptions_by_type[event_type] = dict()
            util.subscriptions_by_type[event_type][subscription_id] = sc

        util.all_subscriptions[subscription_id] = sc

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
        logging.exception('Mapping error: {}'.format(e))
        abort(status.HTTP_400_BAD_REQUEST, e.msg['message'])
    except Exception as e:
        # In case of error print exception and abort
        logging.exception(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
