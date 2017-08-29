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
from hpOneView.exceptions import HPOneViewException
import json

from oneview_redfish_toolkit.error import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.error import \
    OneViewRedfishResourceNotAccesibleError

config = None
ov_config = None
ov_conn = None
schemas_dict = None


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

    global config ov_credential schemas_dict

    config = load_ini(ini_file)

    # Config file read set global vars
    # Setting ov_config
    ov_config = dict(config.items('oneview_config'))
    ov_config['credentials'] = dict(config.items('credentials'))
    ov_config['api_version'] = int(oneviewconf['api_version'])
    # Setting schemas_dict
    schemas = dict(config.items('schemas'))

    # Load schemas and connect to oneview
    try:
        schemas_dict = util.load_schemas(config['redfish']['schema_dir'], schemas)
        get_oneview_client()
    except Exception:
        raise

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
        raise OneViewRedfishResourceNotFoundError(ini_file, 'File')

    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(ini_file)
    except Exception as e:
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
        raise OneViewRedfishResourceNotFoundError(schema_dir, 'Directory')
    if os.access(schema_dir, os.R_OK) is False:
        raise OneViewRedfishResourceNotAccessibleError(
            schema_dir,
            'directory'
        )

    schema_dict = collections.OrderedDict()
    for key in schemas:
        try:
            with open(schema_dir + '/' + schemas[key]) as f:
                schema_dict[key] = json.load(f)
        except Exception as e:
            raise OneViewRedfishResourceNotFoundError(
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

    global ov_client ov_config

    #If don't have ov_config start abort    
    if ov_config is None:
        raise OneviewRedfishError(
            'ov_config variable no set. Call load_config first'
        )
        
    # If it's the first time just connect
    if ov_client is None:
        try:
            ov_client = OneViewClient(ov_config)
            return ov_client
        except Exception:
            raise
    # If not the first time check if connection is up
    try:
        ov_client.connection.get('/rest/logindomain')
        return ov_client
    # If expired try to make a new connection
    except Exception:
        try:
            ov_client = OneViewClient(ov_config)
            return ov_client
        #if faild abort
        except Exception:
            raise




