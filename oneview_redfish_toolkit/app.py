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
import argparse
import ipaddress
import logging
import os
from threading import Thread

# 3rd party libs
from flask import abort
from flask import Flask
from flask import g
from flask import request
from flask import Response
from flask_api import status

# own libs
from hpOneView import HPOneViewException

from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit.blueprints.chassis import chassis
from oneview_redfish_toolkit.blueprints.chassis_collection \
    import chassis_collection
from oneview_redfish_toolkit.blueprints.composition_service \
    import composition_service
from oneview_redfish_toolkit.blueprints.computer_system import computer_system
from oneview_redfish_toolkit.blueprints.computer_system_collection \
    import computer_system_collection
from oneview_redfish_toolkit.blueprints.event_service import event_service
from oneview_redfish_toolkit.blueprints.manager import manager
from oneview_redfish_toolkit.blueprints.manager_collection \
    import manager_collection
from oneview_redfish_toolkit.blueprints.metadata import metadata
from oneview_redfish_toolkit.blueprints.network_adapter \
    import network_adapter
from oneview_redfish_toolkit.blueprints.network_adapter_collection \
    import network_adapter_collection
from oneview_redfish_toolkit.blueprints.network_device_function \
    import network_device_function
from oneview_redfish_toolkit.blueprints.network_device_function_collection \
    import network_device_function_collection
from oneview_redfish_toolkit.blueprints.network_interface \
    import network_interface
from oneview_redfish_toolkit.blueprints.network_interface_collection \
    import network_interface_collection
from oneview_redfish_toolkit.blueprints.network_port import network_port
from oneview_redfish_toolkit.blueprints.network_port_collection \
    import network_port_collection
from oneview_redfish_toolkit.blueprints.odata import odata
from oneview_redfish_toolkit.blueprints.redfish_base import redfish_base
from oneview_redfish_toolkit.blueprints.resource_block import resource_block
from oneview_redfish_toolkit.blueprints.resource_block_collection \
    import resource_block_collection
from oneview_redfish_toolkit.blueprints.service_root import service_root
from oneview_redfish_toolkit.blueprints.session import session
from oneview_redfish_toolkit.blueprints.storage import storage
from oneview_redfish_toolkit.blueprints.storage_collection \
    import storage_collection
from oneview_redfish_toolkit.blueprints.storage_composition_details import \
    storage_composition_details
from oneview_redfish_toolkit.blueprints.subscription\
    import subscription
from oneview_redfish_toolkit.blueprints.subscription_collection \
    import subscription_collection
from oneview_redfish_toolkit.blueprints.thermal import thermal
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder
from oneview_redfish_toolkit.blueprints.zone import zone
from oneview_redfish_toolkit.blueprints.zone_collection import zone_collection
from oneview_redfish_toolkit import util


def main(config_file_path, logging_config_file_path):
    # Load config file, schemas and creates a OV connection
    try:
        util.configure_logging(logging_config_file_path)
        util.load_config(config_file_path)
    except Exception as e:
        logging.exception('Failed to load app configuration')
        logging.exception(e)
        exit(1)

    # Check auth mode
    auth_mode = util.config.get('redfish', 'authentication_mode')

    if auth_mode not in ["conf", "session"]:
        logging.error(
            "Invalid authentication_mode. Please check your conf"
            " file. Valid values are 'conf' or 'session'")

    # Flask application
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(redfish_base, url_prefix="/redfish/")
    app.register_blueprint(service_root, url_prefix='/redfish/v1/')
    app.register_blueprint(chassis_collection)
    app.register_blueprint(computer_system_collection)
    app.register_blueprint(computer_system)
    app.register_blueprint(composition_service)
    app.register_blueprint(chassis)
    app.register_blueprint(manager_collection)
    app.register_blueprint(manager)
    app.register_blueprint(metadata)
    app.register_blueprint(odata)
    app.register_blueprint(storage)
    app.register_blueprint(thermal)
    app.register_blueprint(storage_collection)
    app.register_blueprint(network_adapter_collection)
    app.register_blueprint(network_interface_collection)
    app.register_blueprint(network_port_collection)
    app.register_blueprint(network_device_function_collection)
    app.register_blueprint(network_device_function)
    app.register_blueprint(network_interface)
    app.register_blueprint(network_adapter)
    app.register_blueprint(network_port)
    app.register_blueprint(session)
    app.register_blueprint(storage_composition_details)
    app.register_blueprint(resource_block_collection)
    app.register_blueprint(resource_block)
    app.register_blueprint(zone_collection)
    app.register_blueprint(zone)

    if auth_mode == "conf":
        app.register_blueprint(event_service)
        app.register_blueprint(subscription_collection)
        app.register_blueprint(subscription)

    @app.before_request
    def check_authentication():
        """Checks authentication before serving the request"""
        # If authentication_mode = conf don't need auth
        auth_mode = util.config["redfish"]["authentication_mode"]
        if auth_mode == "conf":
            g.oneview_client = util.get_oneview_client()
            return None
        else:
            # ServiceRoot don't need auth
            if request.path.rstrip("/") in {"/redfish/v1",
                                            "/redfish",
                                            "/redfish/v1/odata",
                                            "/redfish/v1/$metadata"}:
                g.oneview_client = util.get_oneview_client(None, True)
                return None
            # If authenticating we do nothing
            if request.path == "/redfish/v1/SessionService/Sessions" and \
                request.method == "POST":
                return None
            # Any other path we demand auth
            x_auth_token = request.headers.get('x-auth-token')
            if not x_auth_token:
                abort(
                    status.HTTP_401_UNAUTHORIZED,
                    "x-auth-token header not found")
            else:
                try:
                    oneview_client = util.get_oneview_client(x_auth_token)
                    g.oneview_client = oneview_client
                except Exception:
                    abort(status.HTTP_401_UNAUTHORIZED, "invalid auth token")

    @app.before_request
    def has_odata_version_header():
        """Deny request that specify a different OData-Version than 4.0"""
        odata_version_header = request.headers.get("OData-Version")

        if odata_version_header is None:
            pass
        elif odata_version_header != "4.0":
            abort(status.HTTP_412_PRECONDITION_FAILED,
                  "The request specify a different OData-Version "
                  "header then 4.0. This server also responds "
                  "to requests without the OData-Version header")

    @app.after_request
    def set_odata_version_header(response):
        """Set OData-Version header for all responses"""
        response.headers["OData-Version"] = "4.0"
        return response

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

    @app.errorhandler(status.HTTP_401_UNAUTHORIZED)
    def unauthorized_error(error):
        """Creates a Unauthorized Error response"""
        redfish_error = RedfishError(
            "GeneralError", error.description)

        error_str = redfish_error.serialize()
        return Response(
            response=error_str,
            status=status.HTTP_401_UNAUTHORIZED,
            mimetype='application/json')

    @app.errorhandler(status.HTTP_404_NOT_FOUND)
    def not_found(error):
        """Creates a Not Found Error response"""
        return ResponseBuilder.error_404(error)

    @app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server_error(error):
        """Creates an Internal Server Error response"""
        return ResponseBuilder.error_500(error)

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

    @app.errorhandler(HPOneViewException)
    def hp_oneview_client_exception(exception):
        return ResponseBuilder.error_by_hp_oneview_exception(exception)

    if util.config['redfish']['authentication_mode'] == 'conf':
        # Loading scmb connection
        if scmb.check_cert_exist():
            logging.info('SCMB certs already exists testing connection...')
        else:
            logging.info('SCMB certs not found. Generating/getting certs....')
            scmb.get_cert()
            logging.info('Got certs. Testing connection...')
        if not scmb.is_cert_working_with_scmb():
            logging.error('Failed to connect to scmb. Aborting...')
            exit(1)
        scmb_thread = Thread(target=scmb.listen_scmb)
        scmb_thread.daemon = True
        scmb_thread.start()
    else:
        logging.warning("Authentication mode set to session. SCMB events will "
                        "be disabled")

    config = util.config

    try:
        host = config["redfish"]["redfish_host"]

        # Gets the correct IP type based on the string
        ipaddress.ip_address(host)
    except ValueError:
        logging.error("Informed IP is not valid. Check the "
                      "variable 'redfish_host' on your config file.")
        exit(1)

    try:
        port = int(config["redfish"]["redfish_port"])
    except Exception:
        logging.exception(
            "Port must be an integer number between 1 and 65536.")
        exit(1)
    # Checking port range
    if port < 1 or port > 65536:
        logging.error("Port must be an integer number between 1 and 65536.")
        exit(1)

    if config["ssl"]["SSLType"] in ("self-signed", "adhoc"):
        logging.warning("Server is starting with a self-signed certificate.")
    if config["ssl"]["SSLType"] == "disabled":
        logging.warning(
            "Server is starting in HTTP mode. This is an insecure mode. "
            "Running the server with HTTPS enabled is highly recommended.")

    ssl_type = config["ssl"]["SSLType"]
    # Check SSLType:
    if ssl_type not in ('disabled', 'adhoc', 'certs', 'self-signed'):
        logging.error(
            "Invalid SSL type: {}. Must be one of: disabled, adhoc, "
            "self-signed or certs".
            format(ssl_type))
        exit(1)

    try:
        debug = config["redfish"]["debug"]

        if debug not in ('false', 'true'):
            logging.warning(
                "Debug option must be either \'true\' or \'false\'. "
                "Defaulting to \'false\'.")
            debug = False
        else:
            debug = (debug == "true")
    except Exception:
        logging.warning(
            "Invalid debug configuration. "
            "Defaulting to \'false\'.")
        debug = False

    if ssl_type == 'disabled':
        app.run(host=host, port=port, debug=debug)
    elif ssl_type == 'adhoc':
        app.run(host=host, port=port, debug=debug, ssl_context="adhoc")
    else:
        # We should use certs file provided by the user
        ssl_cert_file = config["ssl"]["SSLCertFile"]
        ssl_key_file = config["ssl"]["SSLKeyFile"]
        # Generating cert files if they don't exists
        if ssl_type == "self-signed":
            if not os.path.exists(ssl_cert_file) and not \
                os.path.exists(ssl_key_file):
                logging.warning("Generating self-signed certs")
                # Generate certificates
                util.generate_certificate(
                    os.path.dirname(ssl_cert_file), "self-signed", 2048)
            else:
                logging.warning("Using existing self-signed certs")

        if ssl_cert_file == "" or ssl_key_file == "":
            logging.error(
                "SSL type: is 'cert' but one of the files are missing on"
                "the config file. SSLCertFile: {}, SSLKeyFile: {}.".
                format(ssl_cert_file, ssl_key_file))

        ssl_context = (ssl_cert_file, ssl_key_file)
        app.run(host=host, port=port, debug=debug, ssl_context=ssl_context)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments parser')
    parser.add_argument('--config', type=str,
                        help='A required path to config file')
    parser.add_argument('--log-config', type=str,
                        help='A required path to logging config file')
    args = parser.parse_args()

    main(args.config, args.log_config)
