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
import time

# 3rd party libs
import cherrypy
from cherrypy.process.plugins import Daemonizer
from cherrypy.process.plugins import PIDFile
from flask import abort
from flask import Flask
from flask import g
from flask import request
from flask import Response
from flask_api import status

# own libs
from hpOneView import HPOneViewException
from paste.translogger import TransLogger

from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit.api.session_collection import SessionCollection
from oneview_redfish_toolkit.blueprints.chassis import chassis
from oneview_redfish_toolkit.blueprints.chassis_collection \
    import chassis_collection
from oneview_redfish_toolkit.blueprints.composition_service \
    import composition_service
from oneview_redfish_toolkit.blueprints.computer_system import computer_system
from oneview_redfish_toolkit.blueprints.computer_system_collection \
    import computer_system_collection
from oneview_redfish_toolkit.blueprints.ethernet_interface import \
    ethernet_interface
from oneview_redfish_toolkit.blueprints.ethernet_interface_collection import \
    ethernet_interface_collection
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
from oneview_redfish_toolkit.blueprints.processor import processor
from oneview_redfish_toolkit.blueprints.processor_collection \
    import processor_collection
from oneview_redfish_toolkit.blueprints.redfish_base import redfish_base
from oneview_redfish_toolkit.blueprints.resource_block import resource_block
from oneview_redfish_toolkit.blueprints.resource_block_collection \
    import resource_block_collection
from oneview_redfish_toolkit.blueprints.service_root import service_root
from oneview_redfish_toolkit.blueprints.session import session
from oneview_redfish_toolkit.blueprints.session_service import session_service
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
from oneview_redfish_toolkit.blueprints.vlan_network_interface import \
    vlan_network_interface
from oneview_redfish_toolkit.blueprints.zone import zone
from oneview_redfish_toolkit.blueprints.zone_collection import zone_collection
from oneview_redfish_toolkit import category_resource
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.config import PERFORMANCE_LOGGER_NAME
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import handler_multiple_oneview
from oneview_redfish_toolkit import multiple_oneview
from oneview_redfish_toolkit import util


PID_FILE_NAME = 'toolkit.pid'


def main(config_file_path, logging_config_file_path,
         is_dev_env=False, is_debug_mode=False):
    # Load config file, schemas and creates a OV connection
    try:
        config.configure_logging(logging_config_file_path)
        config.load_config(config_file_path)
    except Exception as e:
        logging.exception('Failed to load app configuration')
        logging.exception(e)
        exit(1)

    # Check auth mode
    auth_mode = config.get_authentication_mode()

    if auth_mode not in ["conf", "session"]:
        logging.error(
            "Invalid authentication_mode. Please check your conf"
            " file. Valid values are 'conf' or 'session'")

    # Flask application
    app = Flask(__name__)

    app.url_map.strict_slashes = False

    # Register blueprints
    app.register_blueprint(redfish_base, url_prefix="/redfish/")
    app.register_blueprint(service_root, url_prefix='/redfish/v1/')
    app.register_blueprint(event_service)
    app.register_blueprint(session_service)
    app.register_blueprint(chassis_collection)
    app.register_blueprint(computer_system_collection)
    app.register_blueprint(computer_system)
    app.register_blueprint(composition_service)
    app.register_blueprint(chassis)
    app.register_blueprint(ethernet_interface)
    app.register_blueprint(ethernet_interface_collection)
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
    app.register_blueprint(processor)
    app.register_blueprint(processor_collection)
    app.register_blueprint(storage_composition_details)
    app.register_blueprint(resource_block_collection)
    app.register_blueprint(resource_block)
    app.register_blueprint(vlan_network_interface)
    app.register_blueprint(zone_collection)
    app.register_blueprint(zone)

    # Init cached data
    client_session.init_map_clients()
    client_session.init_gc_for_expired_sessions()
    multiple_oneview.init_map_resources()
    multiple_oneview.init_map_appliances()
    category_resource.init_map_category_resources()

    if auth_mode == "conf":
        app.register_blueprint(subscription_collection)
        app.register_blueprint(subscription)

        client_session.login_conf_mode()
    else:
        app.register_blueprint(session)

    @app.before_request
    def init_performance_data():
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            g.start_time_req = time.time()
            g.elapsed_time_ov = 0

    @app.before_request
    def check_authentication():
        # If authenticating do not check for anything
        if request.url_rule and \
           request.url_rule.rule == SessionCollection.BASE_URI and \
           request.method == "POST":
            return None

        if connection.is_service_root():
            return None

        if config.auth_mode_is_session():
            x_auth_token = request.headers.get('x-auth-token')
            client_session.check_authentication(x_auth_token)

        g.oneview_client = \
            handler_multiple_oneview.MultipleOneViewResource()

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

    @app.after_request
    def log_performance_data(response):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            end_time = time.time()
            req_time = end_time - g.start_time_req
            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "OneView process: " + str(g.elapsed_time_ov))
            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "Redfish process: " + str(req_time - g.elapsed_time_ov))
            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "Total process: " + str(req_time))
        return response

    @app.errorhandler(status.HTTP_400_BAD_REQUEST)
    def bad_request(error):
        """Creates a Bad Request Error response"""
        logging.error(error.description)

        redfish_error = RedfishError(
            "PropertyValueNotInList", error.description)

        # TODO(karolcatunda) Improve args passed to add_extended_info method
        # redfish_error.add_extended_info()

        error_str = redfish_error.serialize()
        return Response(
            response=error_str,
            status=status.HTTP_400_BAD_REQUEST,
            mimetype='application/json')

    @app.errorhandler(status.HTTP_401_UNAUTHORIZED)
    def unauthorized_error(error):
        """Creates a Unauthorized Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_401(error)

    @app.errorhandler(status.HTTP_403_FORBIDDEN)
    def forbidden(error):
        """Creates a Forbidden Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_403(error)

    @app.errorhandler(status.HTTP_404_NOT_FOUND)
    def not_found(error):
        """Creates a Not Found Error response"""
        logging.error(error.description)

        return ResponseBuilder.error_404(error)

    @app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server_error(error):
        """Creates an Internal Server Error response"""
        logging.error(error)

        return ResponseBuilder.error_500(error)

    @app.errorhandler(status.HTTP_501_NOT_IMPLEMENTED)
    def not_implemented(error):
        """Creates a Not Implemented Error response"""
        logging.error(error.description)

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
        logging.exception(exception)
        response = ResponseBuilder.error_by_hp_oneview_exception(exception)

        # checking if session has expired on Oneview
        if config.auth_mode_is_session() and \
                response.status_code == status.HTTP_401_UNAUTHORIZED:
            token = request.headers.get('x-auth-token')
            client_session.clear_session_by_token(token)

        return response

    scmb.init_event_service()

    app_config = config.get_config()

    try:
        host = app_config["redfish"]["redfish_host"]

        # Gets the correct IP type based on the string
        ipaddress.ip_address(host)
    except ValueError:
        logging.error("Informed IP is not valid. Check the "
                      "variable 'redfish_host' on your config file.")
        exit(1)

    try:
        port = int(app_config["redfish"]["redfish_port"])
    except Exception:
        logging.exception(
            "Port must be an integer number between 1 and 65536.")
        exit(1)
    # Checking port range
    if port < 1 or port > 65536:
        logging.error("Port must be an integer number between 1 and 65536.")
        exit(1)

    if app_config["ssl"]["SSLType"] in ("self-signed", "adhoc"):
        logging.warning("Server is starting with a self-signed certificate.")
    if app_config["ssl"]["SSLType"] == "disabled":
        logging.warning(
            "Server is starting in HTTP mode. This is an insecure mode. "
            "Running the server with HTTPS enabled is highly recommended.")

    ssl_type = app_config["ssl"]["SSLType"]
    # Check SSLType:
    if ssl_type not in ('disabled', 'adhoc', 'certs', 'self-signed'):
        logging.error(
            "Invalid SSL type: {}. Must be one of: disabled, adhoc, "
            "self-signed or certs".
            format(ssl_type))
        exit(1)

    if ssl_type == 'disabled':
        app.run(host=host, port=port, debug=is_debug_mode)
    elif ssl_type == 'adhoc':
        app.run(host=host, port=port, debug=is_debug_mode, ssl_context="adhoc")
    else:
        # We should use certs file provided by the user
        ssl_cert_file = app_config["ssl"]["SSLCertFile"]
        ssl_key_file = app_config["ssl"]["SSLKeyFile"]

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
        elif ssl_cert_file == "" or ssl_key_file == "":
            logging.error(
                "SSL type: is 'cert' but one of the files are missing on"
                "the config file. SSLCertFile: {}, SSLKeyFile: {}.".format(
                    ssl_cert_file, ssl_key_file))

        if is_dev_env and is_debug_mode:
            ssl_context = (ssl_cert_file, ssl_key_file)
            app.run(host=host, port=port, debug=is_debug_mode,
                    ssl_context=ssl_context)
        else:
            start_cherrypy(app,
                           host=host,
                           port=port,
                           ssl_cert_file=ssl_cert_file,
                           ssl_key_file=ssl_key_file,
                           is_dev_env=is_dev_env)


def start_cherrypy(app,
                   host=None,
                   port=None,
                   ssl_cert_file=None,
                   ssl_key_file=None,
                   is_dev_env=None):

    if not is_dev_env:
        cherrypy.config.update({'environment': 'production'})

    cherrypy.config.update(config.get_cherrypy_config())

    cherrypy.config.update({
        'log.screen': False,
        'server.socket_port': port,
        'server.socket_host': host,
        'server.ssl_certificate': ssl_cert_file,
        'server.ssl_private_key': ssl_key_file
    })

    app_logged = TransLogger(app.wsgi_app, setup_console_handler=False)
    cherrypy.tree.graft(app_logged, '/')

    if not is_dev_env:
        Daemonizer(cherrypy.engine).subscribe()
        PIDFile(cherrypy.engine, os.path.join(util.get_user_directory(),
                                              PID_FILE_NAME)).subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments parser')
    parser.add_argument('--config', type=str,
                        help='A required path to config file')
    parser.add_argument('--log-config', type=str,
                        help='A required path to logging config file')
    parser.add_argument('--dev', type=bool, nargs='?',
                        default=False, const=True,
                        help='Optional value to tell the application to run '
                             'in development mode.')
    parser.add_argument('--debug', type=bool, nargs='?',
                        default=False, const=True,
                        help='Optional value to tell the application to run '
                             'in debug mode, this option only is valid when '
                             'the development mode is set too, otherwise '
                             'it is ignored.')
    args = parser.parse_args()

    main(args.config, args.log_config,
         is_dev_env=args.dev, is_debug_mode=args.debug)
