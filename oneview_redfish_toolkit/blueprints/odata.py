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

# own libs
from oneview_redfish_toolkit.api.odata import Odata

odata = Blueprint('odata', __name__)


@odata.route('/redfish/v1/odata', methods=["GET"])
def get_odata():
    """Gets Odata

        List the services offered by this server
    """

    try:
        odt = Odata()
        json_str = odt.serialize()
        return Response(
            response=json_str,
            status=200,
            mimetype='application/json')
    except Exception as e:
        logging.exception('Odata error: {}'.format(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
