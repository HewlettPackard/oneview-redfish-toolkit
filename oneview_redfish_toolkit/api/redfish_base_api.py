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

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask_api import status

redfish_base = Blueprint("redfish_base", __name__, url_prefix="/redfish")


@redfish_base.route("/", methods=["GET"])
def get_redfish_base():
    """Get JSON with Redfish version.

    :return: Redfish version route.
    :rtype: JSON
    """
    return make_response(jsonify({"v1": "/redfish/v1/"}), status.HTTP_200_OK)


@redfish_base.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Improve not found error message.

    :param error: Flask error.
    :return: Error message.
    :rtype: JSON
    """
    return make_response(jsonify({"error": "Redfish base not found."}),
                         status.HTTP_404_NOT_FOUND)
