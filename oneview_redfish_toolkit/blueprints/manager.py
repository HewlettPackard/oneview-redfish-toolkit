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
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.manager import Manager
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit.services.manager_service import \
    get_oneview_ip_by_manager_uuid

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
        state_url = "/controller-state.json"
        ov_health_status_url = "/rest/appliance/health-status"

        ov_ip = get_oneview_ip_by_manager_uuid(uuid)
        if not ov_ip:
            abort(status.HTTP_404_NOT_FOUND,
                  "Manager with id {} was not found".format(uuid))

        ov_client = client_session.get_oneview_client(ov_ip)

        ov_appliance_info = multiple_oneview.execute_query_ov_client(
            ov_client, "appliance_node_information", "get_version"
        )
        ov_appliance_state = multiple_oneview.execute_query_ov_client(
            ov_client, "connection", "get", state_url
        )
        ov_appliance_health_status = multiple_oneview.execute_query_ov_client(
            ov_client, "connection", "get", ov_health_status_url
        )

        manager = Manager(ov_appliance_info,
                          ov_appliance_state,
                          ov_appliance_health_status
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
