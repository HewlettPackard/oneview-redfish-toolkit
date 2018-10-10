# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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
import os

# Modules own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotAccessibleError
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api import schemas
from oneview_redfish_toolkit import connection
from oneview_redfish_toolkit import util


API_VERSION = 600

COUNTER_LOGGER_NAME = 'qtty'
PERFORMANCE_LOGGER_NAME = 'perf'
ONEVIEW_SDK_LOGGER_NAME = 'ovData'


# Globals vars:
#   globals()['config']
#   globals()['registry_dict']
#   globals()['stored_schemas']


def get_config():
    return globals()['config']


def get_oneview_config():
    return dict(get_config().items('oneview_config'))


def get_oneview_multiple_ips():
    ips_config = dict(get_config().items('oneview_config'))['ip'].split(",")
    list_ips = [ip.strip() for ip in ips_config]
    return list_ips


def get_credentials():
    return dict(get_config().items('credentials'))


def get_authentication_mode():
    return get_config().get('redfish', 'authentication_mode')


def auth_mode_is_session():
    return get_authentication_mode() == 'session'


def auth_mode_is_conf():
    return get_authentication_mode() == 'conf'


def get_cherrypy_config():
    cherrypy_config = dict(get_config().items('cherrypy_config'))

    for key, val in cherrypy_config.items():
        if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
            cherrypy_config[key] = int(val)

    return cherrypy_config


def get_registry_dict():
    return globals()['registry_dict']


def get_stored_schemas():
    return globals()['stored_schemas']


def get_api_version():
    return API_VERSION


def get_composition_settings():
    return dict(get_config().items('redfish-composition'))


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

    config = load_conf_file(conf_file)
    globals()['config'] = config

    # Config file read set global vars
    # Setting ov_config
    # ov_config = dict(config.items('oneview_config'))
    # ov_config['credentials'] = dict(config.items('credentials'))
    # ov_config['api_version'] = API_VERSION
    # globals()['ov_config'] = ov_config

    util.load_event_service_info()

    # Load schemas | Store schemas
    try:
        for ip_oneview in get_oneview_multiple_ips():
            connection.check_oneview_availability(ip_oneview)

        registry_dict = load_registry(
            get_registry_path(),
            schemas.REGISTRY)
        globals()['registry_dict'] = registry_dict

        load_schemas(get_schemas_path())
    except OneViewRedfishResourceNotFoundError as e:
        raise OneViewRedfishError(
            'Failed to load schemas or registries: {}'.format(e)
        )
    except Exception as e:
        raise OneViewRedfishError(
            'Failed to connect to OneView: {}'.format(e)
        )


def load_conf_file(conf_file):
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


def load_registry(registry_dir, registries):
    """Loads Registries

        Loads all registries using registry_dir directory

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


def load_schemas(schema_dir):
    """Load all DMTF JSON Schemas

        Load all schemas listed in schemas searching schema_dir directory.

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


def get_registry_path():
    source = util.get_app_path()
    return os.path.join(source, "registry")


def get_schemas_path():
    source = util.get_app_path()
    return os.path.join(source, "schemas")
