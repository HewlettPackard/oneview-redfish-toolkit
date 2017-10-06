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
from flask import Response
from flask_api import status
from hpOneView.exceptions import HPOneViewException

# Own libs
from oneview_redfish_toolkit.api.blade_manager import BladeManager
from oneview_redfish_toolkit.api.enclosure_manager import EnclosureManager
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import util

manager = Blueprint("manager", __name__)


@manager.route("/redfish/v1/Managers/<uuid>", methods=["GET"])
def get_managers(uuid):
    """Get the Redfish Managers.

        Get method to return Managers JSON when
        /redfish/v1/Managers/id is requested.

        Returns:
            JSON: JSON with Managers info for Enclosure or ServerHardware.
    """
    try:
        oneview_client = util.get_oneview_client()

        appliance_information = \
            oneview_client.appliance_node_information.get_version()
        oneview_version = appliance_information['softwareVersion']

        resource_index = oneview_client.index_resources.get_all(
            filter='uuid=' + uuid
        )

        if resource_index:
            category = resource_index[0]["category"]
        else:
            raise OneViewRedfishError('Cannot find Index resource')

        if category == 'server-hardware':
            server_hardware = oneview_client.server_hardware.get(uuid)
            manager = BladeManager(server_hardware)
        elif category == 'enclosures':
            enclosure = oneview_client.enclosures.get(uuid)
            manager = EnclosureManager(enclosure, oneview_version)
        else:
            raise OneViewRedfishError('Enclosure type not found')

        json_str = manager.serialize()

        return Response(
            response=json_str,
            status=status.HTTP_200_OK,
            mimetype="application/json")
    except HPOneViewException as e:
        # In case of error log exception and abort
        logging.error(e)
        abort(status.HTTP_404_NOT_FOUND, "Manager not found")

    except OneViewRedfishError as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_404_NOT_FOUND, e.msg)

    except Exception as e:
        # In case of error log exception and abort
        logging.error('Unexpected error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
