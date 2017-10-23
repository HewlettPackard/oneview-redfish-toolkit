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
import os

# 3rd party libs
from flask import Flask
from flask import Response
from flask_api import status

# own libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints.chassis import chassis
from oneview_redfish_toolkit.blueprints.chassis_collection \
    import chassis_collection
from oneview_redfish_toolkit.blueprints.computer_system import computer_system
from oneview_redfish_toolkit.blueprints.computer_system_collection \
    import computer_system_collection
from oneview_redfish_toolkit.blueprints.manager import manager
from oneview_redfish_toolkit.blueprints.manager_collection \
    import manager_collection
from oneview_redfish_toolkit.blueprints.network_device_function_collection \
    import network_device_function_collection
from oneview_redfish_toolkit.blueprints.network_interface \
    import network_interface
from oneview_redfish_toolkit.blueprints.network_interface_collection \
    import network_interface_collection
from oneview_redfish_toolkit.blueprints.network_port_collection \
    import network_port_collection
from oneview_redfish_toolkit.blueprints.odata import odata
from oneview_redfish_toolkit.blueprints.redfish_base import redfish_base
from oneview_redfish_toolkit.blueprints.service_root import service_root
from oneview_redfish_toolkit.blueprints.storage import storage
from oneview_redfish_toolkit.blueprints.storage_collection \
    import storage_collection
from oneview_redfish_toolkit.blueprints.thermal import thermal
from oneview_redfish_toolkit import util


util.configure_logging(os.getenv("LOGGING_FILE", "logging.conf"))

# Load config file, schemas and creates a OV connection
try:
    util.load_config('redfish.conf')
except Exception as e:
    logging.error('Failed to load app configuration')
    logging.error(e)
    exit(1)

# Flask application
app = Flask(__name__)

# Register blueprints
app.register_blueprint(redfish_base, url_prefix="/redfish/")
app.register_blueprint(service_root, url_prefix='/redfish/v1/')
app.register_blueprint(chassis_collection)
app.register_blueprint(computer_system_collection)
app.register_blueprint(computer_system)
app.register_blueprint(chassis)
app.register_blueprint(manager_collection)
app.register_blueprint(manager)
app.register_blueprint(odata)
app.register_blueprint(storage)
app.register_blueprint(thermal)
app.register_blueprint(storage_collection)
app.register_blueprint(network_interface_collection)
app.register_blueprint(network_port_collection)
app.register_blueprint(network_device_function_collection)
app.register_blueprint(network_interface)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """Creates a Bad Request Error response"""
    redfish_error = RedfishError(
        "PropertyValueNotInList", error.description)

    redfish_error.add_extended_info(
        message_id="PropertyValueNotInList",
        message_args=["VALUE", "PROPERTY"],
        related_properties=["PROPERTY"])

    error_str = redfish_error.serialize()
    return Response(
        response=error_str,
        status=status.HTTP_400_BAD_REQUEST,
        mimetype='application/json')


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Creates a Not Found Error response"""
    redfish_error = RedfishError(
        "GeneralError", error.description)
    error_str = redfish_error.serialize()
    return Response(
        response=error_str,
        status=status.HTTP_404_NOT_FOUND,
        mimetype='application/json')


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Creates an Internal Server Error response"""

    redfish_error = RedfishError(
        "InternalError",
        "The request failed due to an internal service error.  "
        "The service is still operational.")
    redfish_error.add_extended_info("InternalError")
    error_str = redfish_error.serialize()
    return Response(
        response=error_str,
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        mimetype="application/json")


@app.errorhandler(status.HTTP_501_NOT_IMPLEMENTED)
def not_implemented(error):
    """Creates a Not Implemented Error response"""
    redfish_error = RedfishError(
        "ActionNotSupported", error.description)
    redfish_error.add_extended_info(
        message_id="ActionNotSupported",
        message_args=["action"])

    error_str = redfish_error.serialize()
    return Response(
        response=error_str,
        status=status.HTTP_501_NOT_IMPLEMENTED,
        mimetype='application/json')

config = util.config

try:
    port = int(config["redfish"]["redfish_port"])
except Exception:
    logging.error("Port must be an integer number between 1 and 65536")
    exit(1)
# Checking port range
if port < 1 or port > 65536:
    logging.error("Port must be an integer number between 1 and 65536")
    exit(1)

ssl_type = config["ssl"]["SSLType"]
# Check SSLType:
if ssl_type not in ('disabled', 'adhoc', 'certs'):
    logging.error(
        "Invalid SSL type: {}. Must be one of: disabled, adhoc or certs".
        format(ssl_type))
    exit(1)

if ssl_type == 'disabled':
    app.run(host="0.0.0.0", port=port, debug=True)
elif ssl_type == 'adhoc':
    app.run(host="0.0.0.0", port=port, debug=True, ssl_context="adhoc")
else:
    # We should use certs file provided by the user
    ssl_cert_file = config["ssl"]["SSLCertFile"]
    ssl_key_file = config["ssl"]["SSLKeyFile"]
    if ssl_cert_file == "" or ssl_key_file == "":
        logging.error(
            "SSL type: is 'cert' but one of the files are missing on"
            "the config file. SSLCertFile: {}, SSLKeyFile: {}.".
            format(ssl_cert_file, ssl_key_file))

    ssl_context = (ssl_cert_file, ssl_key_file)
    app.run(host="0.0.0.0", port=port, debug=True, ssl_context=ssl_context)
