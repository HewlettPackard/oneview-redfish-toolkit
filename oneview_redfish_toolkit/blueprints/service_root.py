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

# own libs
from hpOneView.exceptions import HPOneViewException
from oneview_redfish_toolkit.api.service_root import ServiceRoot

service_root = Blueprint('service_root', __name__)


@service_root.route('/', methods=["GET"])
def get_service_root():
    """Gets ServiceRoot

        Recover OneView UUID from appliance and creates
        ServiceRoot redfish JSON
    """

    try:
        # Gets serverhardware for given UUID
        appliance_node_information = \
            g.oneview_client.appliance_node_information.get_version()
        uuid = appliance_node_information['uuid']

        sr = ServiceRoot(uuid)
        json_str = sr.serialize()
        return Response(
            response=json_str,
            status=200,
            mimetype='application/json')
    except HPOneViewException as e:
        if e.oneview_response['errorCode'] == "RESOURCE_NOT_FOUND":
            logging.exception("Resource not found: {}".format(e))
            abort(status.HTTP_404_NOT_FOUND, "Appliance not found")
        else:
            logging.exception("OneView Exception: {}".format(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logging.exception('ServiceRoot error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
