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
import os

import collections
import configparser
from hpOneView.oneview_client import OneViewClient
import json

from oneview_redfish_toolkit.api import errors


def load_config(ini_file):
    """Loads ini file

        Loads and parser the system ini file into config global var
        Loads json schemas intro schemas_dict global var
        Established a connection with OneView and sets in as ov_conn
        global var

        Args:
            ini_file: string with the ini file name

        Returns:
            None

        Exception:
            OneViewRedfishResourceNotFoundError:
                - if ini file not foud
                - if any of the schemas files are not found
                - if the schema directory is not found
            OneViewRedFishResourceNotAccessibleError:
                - if can't acccess schema's directory
            HPOneViewException:
                - if fails to connect to oneview
    """

    config = load_ini(ini_file)
    globals()['config'] = config

    # Config file read set global vars
    # Setting ov_config
    ov_config = dict(config.items('oneview_config'))
    ov_config['credentials'] = dict(config.items('credentials'))
    ov_config['api_version'] = int(ov_config['api_version'])
    globals()['ov_config'] = ov_config

    # Setting schemas_dict
    schemas = dict(config.items('schemas'))

    # Load schemas and connect to oneview
    try:
        schemas_dict = load_schemas(
            config['redfish']['schema_dir'],
            schemas
        )
        ov_client = OneViewClient(ov_config)
        globals()['schemas_dict'] = schemas_dict
        globals()['ov_client'] = ov_client
    except errors.OneViewRedfishResourceNotFoundError as e:
        raise errors.OneViewRedfishError(
            'Failed to load schemas: {}'.format(e)
        )
    except Exception as e:
        raise errors.OneViewRedfishError(
            'Failed to connect to OneView: {}'.format(e)
        )


def load_ini(ini_file):
    """Loads ini file

        Loads and parses the module ini file

        Args:
            ini_file: string with the ini file name

        Returns:
            configparser object with ini_file configs

        Exception:
            OneViewRedfishResourceNotFoundError:
                - if ini file not foud
    """

    if not os.path.isfile(ini_file):
        raise errors.OneViewRedfishResourceNotFoundError(ini_file, 'File')

    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(ini_file)
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

        Excetions:
            OneviewRedfishResourceNotFoundError:
                - if schema_dir is not found
                - any of json files is not found
            OneviewRedfishResounceNotAccessbile:
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


def get_oneview_client():
    '''Establishes a OneView connction to be used in the module

        Establishes a OV connection if one does not exists.
        If one exists, do a single OV access to check if its sill
        valid. If not tries to establish a new connection.
        Sets the connection on the ov_conn global var

        Args:
            None. Uses global var ov_config which is set by load_config
            with OV configuration and credentials

        Returns:
            OneViewcliente object

        Exceptions:
            HPOpneViewException if can't connect or reconnect to OV
    '''

    ov_client = globals()['ov_client']
    ov_config = globals()['ov_config']

    # Check if connection is ok yet
    try:
        ov_client.connection.get('/rest/logindomains')
        return ov_client
    # If expired try to make a new connection
    except Exception:
        try:
            print('Reautenticou')
            ov_client.connection.login(ov_config['credentials'])
            return ov_client
        # if faild abort
        except Exception:
            raise
