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
import collections
import configparser
import glob
import json
import logging
import logging.config
import OpenSSL
import os
import socket

# 3rd party libs
from hpOneView.oneview_client import OneViewClient

# Modules own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotAccessibleError
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError


globals()['subscriptions_by_type'] = dict()
globals()['all_subscriptions'] = dict()


def configure_logging(log_file_path):
    """Loads logging.conf file

        Loads logging.conf file to create the logger configuration.

        The logger configuration has two handlers, one of stream
        (show logs in the console) and other of file (save a log file)
        where you can choose one of it in [logger_root : handlers].
        In it you can choose the logger level as well.

        Level: Numeric value
        ---------------------
        CRITICAL: 50
        ERROR:    40
        WARNING:  30
        INFO:     20
        DEBUG:    10
        NOTSET:   00
        ---------------------

        How to use: import logging and logging.exception('message')

        Args:
            log_file_path: logging.conf path.

        Exception:
            Exception: if logging.conf file not found.
    """
    if os.path.isfile(log_file_path) is False:
        raise Exception("Config file {} not found".format(log_file_path))
    else:
        logging.config.fileConfig(log_file_path)


def load_config(conf_file):
    """Loads redfish.conf file

        Loads and parsers the system conf file into config global var
        Loads json schemas into schemas_dict global var
        Established a connection with OneView and sets in as ov_conn
        global var

        Args:
            conf_file: string with the conf file name

        Returns:
            None

        Exception:
            OneViewRedfishResourceNotFoundError:
                - if conf file not found
                - if any of the schemas files are not found
                - if the schema directory is not found
            OneViewRedFishResourceNotAccessibleError:
                - if can't access schema's directory
            HPOneViewException:
                - if fails to connect to oneview
    """

    config = load_conf(conf_file)
    globals()['config'] = config

    # Config file read set global vars
    # Setting ov_config
    ov_config = dict(config.items('oneview_config'))
    ov_config['credentials'] = dict(config.items('credentials'))
    ov_config['api_version'] = int(ov_config['api_version'])
    globals()['ov_config'] = ov_config

    # Setting schemas_dict
    schemas = dict(config.items('schemas'))
    globals()['schemas'] = schemas

    registries = dict(config.items('registry'))

    load_event_service_info()

    # Load schemas | Store schemas | Connect to OneView
    try:
        ov_client = OneViewClient(ov_config)

        globals()['ov_client'] = ov_client

        registry_dict = load_registry(
            config['redfish']['registry_dir'],
            registries)
        globals()['registry_dict'] = registry_dict

        store_schemas(config['redfish']['schema_dir'])
    except OneViewRedfishResourceNotFoundError as e:
        raise OneViewRedfishError(
            'Failed to load schemas or registries: {}'.format(e)
        )
    except Exception as e:
        raise OneViewRedfishError(
            'Failed to connect to OneView: {}'.format(e)
        )


def load_conf(conf_file):
    """Loads and parses conf file

        Loads and parses the module conf file

        Args:
            conf_file: string with the conf file name

        Returns:
            ConfigParser object with conf_file configs

        Exception:
            OneViewRedfishResourceNotFoundError:
                - if conf file not found
    """

    if not os.path.isfile(conf_file):
        raise OneViewRedfishResourceNotFoundError(conf_file, 'File')

    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(conf_file)
    except Exception:
        raise

    return config


def load_event_service_info():
    """Loads Event Service information

        Loads DeliveryRetryAttempts and DeliveryRetryIntervalSeconds
        from CONFIG file and store it in a global var.

        Exceptions:
            OneViewRedfishError: DeliveryRetryAttempts and
            DeliveryRetryIntervalSeconds must be integers greater than zero.
    """
    config = globals()['config']
    event_service = dict(config.items("event_service"))

    try:
        delivery_retry_attempts = \
            int(event_service["DeliveryRetryAttempts"])
        delivery_retry_interval = \
            int(event_service["DeliveryRetryIntervalSeconds"])

        if delivery_retry_attempts <= 0 or delivery_retry_interval <= 0:
            raise OneViewRedfishError(
                "DeliveryRetryAttempts and DeliveryRetryIntervalSeconds must"
                " be an integer greater than zero.")
    except ValueError:
        raise OneViewRedfishError(
            "DeliveryRetryAttempts and DeliveryRetryIntervalSeconds "
            "must be valid integers.")

    globals()['delivery_retry_attempts'] = delivery_retry_attempts
    globals()['delivery_retry_interval'] = delivery_retry_interval


def load_registry(registry_dir, registries):
    """Loads Registries

        Loads all registries listed in the config file using registry_dir
        directory

        Args:
            registry_dir: string with the directory to load registries from
            registries: dict with registry name as key and registry file_name
                as value. The key will also be the key in the returning dict.

        Returns:
            OrderedDict: A dict containing 'RegistryName': registry_obj

        Exceptions:
            OneviewRedfishResourceNotFoundError:
                - if registry_dir is not found
                - any of json files is not found
            OneviewRedfishResourceNotAccessible:
                - if registry_dir is can't be accessed
    """

    if os.path.isdir(registry_dir) is False:
        raise OneViewRedfishResourceNotFoundError(
            registry_dir, 'Directory')
    if os.access(registry_dir, os.R_OK) is False:
        raise OneViewRedfishResourceNotAccessibleError(
            registry_dir, 'directory')

    registries_dict = collections.OrderedDict()
    for key in registries:
        try:
            with open(registry_dir + '/' + registries[key]) as f:
                registries_dict[key] = json.load(f)
        except Exception:
            raise OneViewRedfishResourceNotFoundError(
                registries[key], 'File')

    return registries_dict


def store_schemas(schema_dir):
    """Stores all DMTF JSON Schemas

        Stores all schemas listed in schemas searching schema_dir directory.

        Args:
            schema_dir: String with the directory to load schemas from.

        Returns:
            Dictionary: A dict containing ('http://redfish.dmtf.org/schemas/
                        v1/<schema_file_name>': schema_obj) pairs
    """
    schema_paths = glob.glob(schema_dir + '/*.json')

    if not schema_paths:
        raise OneViewRedfishResourceNotFoundError(
            "JSON Schemas", "File")

    stored_schemas = dict()

    for path in schema_paths:
        with open(path) as schema_file:
            json_schema = json.load(schema_file)

        if os.name == 'nt':
            file_name = path.split('\\')[-1]
        else:
            file_name = path.split('/')[-1]
        stored_schemas["http://redfish.dmtf.org/schemas/v1/" + file_name] = \
            json_schema

    globals()['stored_schemas'] = stored_schemas


def get_oneview_client(session_id=None, is_service_root=False):
    """Establishes a OneView connection to be used in the module

        Establishes a OV connection if one does not exists.
        If one exists, do a single OV access to check if its sill
        valid. If not tries to establish a new connection.
        Sets the connection on the ov_conn global var

        Args:
            session_id: The ID of a valid authenticated session, if the
            authentication_mode is session. Defaults to None.

            is_service_root: Informs if who is calling this function is the
            ServiceRoot blueprint. If true, even if authentication_mode is
            set to session it will use the information on the conf file to
            return a connection.  This is a workaround to allow ServiceRoot
            to retrieve the appliance UUID before user logs in.

        Returns:
            OneViewClient object

        Exceptions:
            HPOneViewException if can't connect or reconnect to OV
    """

    config = globals()['config']

    auth_mode = config["redfish"]["authentication_mode"]

    if auth_mode == "conf" or is_service_root:
        # Doing conf based authentication
        ov_client = globals()['ov_client']
        ov_config = globals()['ov_config']

        # Check if connection is ok yet
        try:
            ov_client.connection.get('/rest/logindomains')
            return ov_client
        # If expired try to make a new connection
        except Exception:
            try:
                logging.exception('Re-authenticated')
                ov_client.connection.login(ov_config['credentials'])
                return ov_client
            # if failed abort
            except Exception:
                raise
    else:
        # Auth mode is session
        oneview_config = dict(config.items('oneview_config'))
        oneview_config['credentials'] = {"sessionID": session_id}
        oneview_config['api_version'] = int(oneview_config['api_version'])
        try:
            oneview_client = OneViewClient(oneview_config)
            oneview_client.connection.get('/rest/logindomains')
            return oneview_client
        except Exception:
            logging.exception("Failed to recover session based connection")
            raise


def get_ip():
    """Tries to detect default route IP Address"""
    s = socket.socket(type=socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except Exception as e:
        logging.exception(e)
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def generate_certificate(dir_name, file_name, key_length, key_type="rsa"):
    """Create self-signed cert and key files

        Args:
            dir_name: name of the directory to store the files
            file_name: name of the files that will be created. It will append
                .crt to certificate file and .key to key file
            key_length: key length in bits
            key_type: crypto type: RSA or DSA; defaults to RSA
        Returns:
            Nothing
        Exceptions:
            Raise exceptions on error
    """

    config = globals()['config']
    private_key = OpenSSL.crypto.PKey()
    if key_type == "rsa":
        private_key.generate_key(OpenSSL.crypto.TYPE_RSA, key_length)
    elif key_type == "dsa":
        private_key.generate_key(OpenSSL.crypto.TYPE_DSA, key_length)
    else:
        message = "Invalid key_type"
        logging.error(message)
        raise OneViewRedfishError(message)

    if not config.has_option("ssl-cert-defaults", "commonName"):
        config["ssl-cert-defaults"]["commonName"] = get_ip()

    cert = OpenSSL.crypto.X509()
    cert_subject = cert.get_subject()

    cert_defaults = dict(config.items("ssl-cert-defaults"))

    for key, value in cert_defaults.items():
        setattr(cert_subject, key, value)

    cert.set_serial_number(1)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(private_key)
    cert.sign(private_key, "sha1")

    # Save Files
    with open(os.path.join(dir_name, file_name + ".crt"), "wt") as f:
        f.write(OpenSSL.crypto.dump_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert).decode("UTF-8"))
    with open(os.path.join(dir_name, file_name + ".key"), "wt") as f:
        f.write(OpenSSL.crypto.dump_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, private_key).decode("UTF-8"))
