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
import json
import logging
import logging.config
import OpenSSL
import os
import socket

# 3rd party libs
from hpOneView.oneview_client import OneViewClient

# Modules own libs
from oneview_redfish_toolkit.api import errors


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
    registries = dict(config.items('registry'))

    # Load schemas and connect to oneview
    try:
        schemas_dict = load_schemas(
            config['redfish']['schema_dir'],
            schemas
        )
        ov_client = OneViewClient(ov_config)
        globals()['schemas_dict'] = schemas_dict
        globals()['ov_client'] = ov_client
        registry_dict = load_registry(
            config['redfish']['registry_dir'],
            registries
            )
        globals()['registry_dict'] = registry_dict
    except errors.OneViewRedfishResourceNotFoundError as e:
        raise errors.OneViewRedfishError(
            'Failed to load schemas or registries: {}'.format(e)
        )
    except Exception as e:
        raise errors.OneViewRedfishError(
            'Failed to connect to OneView: {}'.format(e)
        )


def load_conf(conf_file):
    """Loads and parses conf file

        Loads and parses the module conf file

        Args:
            conf_file: string with the conf file name

        Returns:
            configparser object with conf_file configs

        Exception:
            OneViewRedfishResourceNotFoundError:
                - if conf file not found
    """

    if not os.path.isfile(conf_file):
        raise errors.OneViewRedfishResourceNotFoundError(conf_file, 'File')

    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(conf_file)
    except Exception:
        raise

    return config


def load_schemas(schema_dir, schemas):
    """Loads schemas

        Loads all schemas in listed in schemas searching on schema_dir
        directory

        Args:
            schema_dir: string with the directory to load schemas from
            schemas: dict with schema name as key and schema file_name
                as value. The key will also be the key in the returning dict

        Returns:
            OrderedDict: A dict containing ('SchemasName' : schema_obj) pairs

        Exceptions:
            OneviewRedfishResourceNotFoundError:
                - if schema_dir is not found
                - any of json files is not found
            OneviewRedfishResourceNotAccessible:
                - if schema_dir is can't be accessed
    """

    if os.path.isdir(schema_dir) is False:
        raise errors.OneViewRedfishResourceNotFoundError(
            schema_dir,
            'Directory'
        )
    if os.access(schema_dir, os.R_OK) is False:
        raise errors.OneViewRedFishResourceNotAccessibleError(
            schema_dir,
            'directory'
        )

    schema_dict = collections.OrderedDict()
    for key in schemas:
        try:
            with open(schema_dir + '/' + schemas[key]) as f:
                schema_dict[key] = json.load(f)
        except Exception:
            raise errors.OneViewRedfishResourceNotFoundError(
                schemas[key],
                'File'
            )

    return schema_dict


def load_registry(registry_dir, registries):
    """Loads Registries

        Loads all registries listed in the config file using registry_dir
        directory

        Args:
            registry_dir: string with the directory to load registries from
            registries: dict with registry name as key and registry file_name
                as value. The key will also be the key in the returning dict

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
        raise errors.OneViewRedfishResourceNotFoundError(
            registry_dir,
            'Directory'
        )
    if os.access(registry_dir, os.R_OK) is False:
        raise errors.OneViewRedFishResourceNotAccessibleError(
            registry_dir,
            'directory'
        )

    registries_dict = collections.OrderedDict()
    for key in registries:
        try:
            with open(registry_dir + '/' + registries[key]) as f:
                registries_dict[key] = json.load(f)
        except Exception:
            raise errors.OneViewRedfishResourceNotFoundError(
                registries[key],
                'File'
            )

    return registries_dict


def get_oneview_client():
    """Establishes a OneView connection to be used in the module

        Establishes a OV connection if one does not exists.
        If one exists, do a single OV access to check if its sill
        valid. If not tries to establish a new connection.
        Sets the connection on the ov_conn global var

        Args:
            None. Uses global var ov_config which is set by load_config
            with OV configuration and credentials

        Returns:
            OneViewClient object

        Exceptions:
            HPOneViewException if can't connect or reconnect to OV
    """

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
        # if faild abort
        except Exception:
            raise


def get_ip():
    """Tries to detect default route IP Address"""
    s = socket.socket(type=socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        IP = s.getsockname()[0]
    except Exception as e:
        logging.exception(e)
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def generate_certificate(dir_name, file_name, key_length, key_type="rsa"):
    """Create self-signed cert and key files

        Args:
            dir_name: name of the directory to store the files
            file_name: name of the files that will be created. It will append
                .crt to certificate file and .key to key file
            key_length: key length in bits
            key_type: cryto type: RSA or DSA; defaults to RSA
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
        logging.exception(message)
        raise errors.OneViewRedfishError(message)

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
