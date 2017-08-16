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

bp_hello_world_api = Blueprint("hello_world_api", __name__, url_prefix="/api")


@bp_hello_world_api.route("/", methods=["GET"])
def list_server_hardware():
    """Get a Hello World message.

    :return: Hello World message.
    :rtype: JSON
    """
    return make_response(jsonify({"message": "Hello World!"}), 200)


@bp_hello_world_api.errorhandler(404)
def not_found(error):
    """Improve not found error message.

    :param error: Flask error.
    :return: Error message.
    :rtype: JSON
    """
    return make_response(jsonify({"error": "Not Found."}), 404)
