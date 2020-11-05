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

import inspect
import json
import logging
import os
import uuid

from filelock import FileLock
from flask import abort
from flask import Blueprint
from flask import request
from flask import Response
from flask_api import status
from jsonschema.exceptions import ValidationError
import validators

from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit.api.subscription import Subscription
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import util


subscription = Blueprint("subscription", __name__)
REDFISH_TOOLKIT_BASE_DIR = 'oneview_redfish_toolkit'
ALL_SUBSCRIPTION_FILE = 'all_subscription.json'


def _all_subscription_file():
    base_dir = os.path.abspath(os.path.join(
        os.path.dirname(inspect.getfile(inspect.currentframe())), '..'))
    logging.info(base_dir)
    return os.path.join(base_dir, ALL_SUBSCRIPTION_FILE)


def get_file_content():
    file_content = None
    try:
        with open(_all_subscription_file()) as f:
            file_content = json.load(f)
    except Exception as e:
        logging.exception("Error while reading File: " + str(e))

    return file_content


def _get_file_lock():
    lock_path = _all_subscription_file() + '.lock'
    lock = FileLock(lock_path)
    return lock


def _update_all_subscription(file_content):
    try:
        with open(_all_subscription_file(), 'w+') as f:
            f.write(json.dumps(file_content, indent=4))
    except Exception as e:
        raise e


def _add_subscription_to_file(subscription):
    file_content = get_file_content()
    if file_content:
        if not file_content.get('members'):
            # On first subscription request, start SCMB service
            if config.auth_mode_is_session():
                token = request.headers.get('x-auth-token')
                scmb.init_event_service(token)
            else:
                scmb.init_event_service()
        file_content['members'].append(subscription)
        _update_all_subscription(file_content)


def _delete_subscription_from_file(subscription_id):
    file_content = get_file_content()
    if file_content and file_content.get('members'):
        sc = [x for x in file_content.get('members')
              if x['Id'] == subscription_id]
        file_content["members"].remove(sc[0])
        _update_all_subscription(file_content)


def _is_duplicate_subscription(destination):
    file_content = get_file_content()
    if file_content and file_content.get('members'):
        for i in file_content.get('members'):
            if i.get('Destination') == destination:
                return True
    return False


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
            KeyError: When occur a key mapping error.
            return abort(400)

    """

    # get Destination, EventTypes and Context from post
    # generate subscription uuid
    # add subscription in subscriptions_by_type
    # add subscription in all_subscriptions

    try:
        body = request.get_json()
        destination = body["Destination"]

        if not validators.url(destination):
            abort(status.HTTP_400_BAD_REQUEST,
                  "Destination must be an URI.")

        # read all_subscription file and check if destination already present
        is_duplicate = _is_duplicate_subscription(destination)
        if is_duplicate:
            abort(status.HTTP_400_BAD_REQUEST, "Destination is duplicate")

        event_types = body["EventTypes"]

        if not event_types:
            abort(status.HTTP_400_BAD_REQUEST,
                  "EventTypes cannot be empty.")

        context = body.get("Context")
    except KeyError:
        error_message = "Invalid JSON key. The JSON request body " \
                        "must have the keys Destination and EventTypes. " \
                        "The Context is optional."
        abort(status.HTTP_400_BAD_REQUEST, error_message)

    subscription_id = str(uuid.uuid1())

    try:
        # Build Subscription object and validates it
        sc = Subscription(subscription_id, destination,
                          event_types, context)
    except ValidationError:
        error_message = "Invalid EventType. The EventTypes are " \
                        "StatusChange, ResourceUpdated, ResourceAdded, " \
                        "ResourceRemoved and Alert."
        abort(status.HTTP_400_BAD_REQUEST, error_message)

    lock = _get_file_lock()
    lock.acquire()
    try:
        # checking for duplicate subscription again to avoid concurrency issue
        is_duplicate = _is_duplicate_subscription(destination)
        if not is_duplicate:
            # write subscription to the all_subscription.json file
            _add_subscription_to_file(sc.redfish)
            for event_type in sc.get_event_types():
                util.get_subscriptions_by_type(
                    )[event_type][subscription_id] = sc

            util.get_all_subscriptions()[subscription_id] = sc
    except Exception as e:
        logging.exception("Error while adding subscription: " + str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR,
              "Error while adding subscription to the file")
    finally:
        lock.release()
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


@subscription.route(
    "/redfish/v1/EventService/EventSubscriptions/<subscription_id>",
    methods=["DELETE"])
def remove_subscription(subscription_id):
    """Removes a specific Subscription

        Args:
            subscription_id: The Subscription ID.
    """
    lock = _get_file_lock()
    lock.acquire()
    try:
        sc = util.get_all_subscriptions()[subscription_id]
        event_types = sc.get_event_types()

        # delete subscription from all_subscription file
        _delete_subscription_from_file(subscription_id)

        for event in event_types:
            del util.get_subscriptions_by_type()[event][subscription_id]

        del util.get_all_subscriptions()[subscription_id]

        return Response(
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except KeyError as e:
        logging.exception("Subscription not found: " + str(e))
        abort(status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.exception("Error while deleting subscription: " + str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        lock.release()


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


def add_subscription_from_file():
    """Add the Redfish Subscription From File.

        EventTypes:
            - ResourceUpdated
            - ResourceAdded
            - ResourceRemoved
            - Alert

        Returns:
            True: If the read from file is successful

    """
    data = get_file_content()
    if data is None:
        return False

    subscription_data = data["members"]
    if not subscription_data:
        return False
    for single_subscription in subscription_data:
        subscription_id = single_subscription["Id"]
        destination = single_subscription["Destination"]
        event_types = single_subscription["EventTypes"]
        context = single_subscription["Context"]

        sc = Subscription(subscription_id, destination,
                          event_types, context)

        for event_type in sc.get_event_types():
            util.get_subscriptions_by_type()[event_type][subscription_id] = sc

        util.get_all_subscriptions()[subscription_id] = sc

    return True
