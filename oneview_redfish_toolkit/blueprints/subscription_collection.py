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
from flask import Response
from flask_api import status

from oneview_redfish_toolkit.api.subscription_collection \
    import SubscriptionCollection
from oneview_redfish_toolkit import util


subscription_collection = Blueprint("subscription_collection", __name__)


@subscription_collection.route(
    "/redfish/v1/EventService/Subscriptions/", methods=["GET"])
def get_subscription_collection():
    """Get the Redfish Subscription Collection.

        Get method to return SubscriptionCollection JSON when
        /redfish/v1/EventService/Subscriptions is requested.
        Returns:
                JSON: JSON with Event Subscriptions.
    """
    try:
        # Build Subscription Collection object and validates it
        sc = SubscriptionCollection(util.all_subscriptions)

        # Build redfish json
        json_str = sc.serialize()

        # Build response and returns
        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except Exception as e:
        # In case of error print exception and abort
        logging.exception(e)
        return abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
