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
from flask import g
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.manager import Manager
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import multiple_oneview

manager = Blueprint("manager", __name__)


@manager.route("/redfish/v1/Managers/<uuid>", methods=["GET"])
def get_managers(uuid):
    """Get the Redfish Managers.

        Get method to return Managers JSON when
        /redfish/v1/Managers/id is requested.

        Returns:
            JSON: JSON with Managers info.
    """
    try:
        oneview_appliances_version = \
            g.oneview_client.appliance_node_information.get_version()
        ov_appliance_info, appliance_index = \
            _get_appliance_by_uuid(uuid, oneview_appliances_version)

        state_url = "/controller-state.json"
        ov_appliances_state = g.oneview_client.connection.get(state_url)

        ov_health_state_url = "/rest/appliance/health-status"
        ov_appliances_health_status = \
            g.oneview_client.connection.get(ov_health_state_url)

        manager = Manager(ov_appliance_info,
                          ov_appliances_state[appliance_index],
                          ov_appliances_health_status[appliance_index]
                          )

        json_str = manager.serialize()

        response = Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
        return response
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.exception(e)
        abort(status.HTTP_404_NOT_FOUND, "Manager not found")

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)

    except Exception as e:
        # In case of error log exception and abort
        logging.exception('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_appliance_by_uuid(uuid, oneview_appliances):
    appliance = dict()
    appliance_index = 0

    for index, ov_appliance in enumerate(oneview_appliances):
        if ov_appliance["uuid"] == uuid:
            appliance = ov_appliance
            appliance_index = index
            break

    if not appliance:
        raise OneViewRedfishError("Could not find manager with id " + uuid)

    return appliance, appliance_index


def get_current_manager():
    oneview_appliances = \
        g.oneview_client.appliance_node_information.get_version()
    oneview_map_resources = multiple_oneview.get_map_resources()

    current_appliance = next(iter(oneview_map_resources.values()))
    appliance_index = \
        config.get_oneview_multiple_ips().index(current_appliance)

    return oneview_appliances[appliance_index]
