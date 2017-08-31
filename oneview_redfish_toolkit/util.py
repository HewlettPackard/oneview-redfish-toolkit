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
import json

import logging
import logging.config


def configure_logging(log_file_path):
    """Loads logging.ini file

        Loads logging.ini file to create the logger configuration.

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

        How to use: import logging and logging.error('message')

        Args:
            log_file_path: logging.ini path.

        Exception:
            Exception: if logging.ini file not found.
    """
    if os.path.isfile(log_file_path) is False:
        raise Exception("Ini file {} not found".format(log_file_path))
    else:
        logging.config.fileConfig(log_file_path)


def load_config(ini_file):
    """Loads ini file

        Loads and parser the system ini file. The default file is redfish.ini.
        Ini file keys are keep their cases.

        Args:
            ini_file: string with the ini file name

        Returns:
            If fails: print a error message and returns False
            If succeed: ConfigParser object with init file contents
    """

    if os.path.isfile(ini_file) is False:
        logging.error("Ini file {} not found".format(ini_file))
        return None
    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(ini_file)
    except Exception as e:
        logging.error(e)
        return None
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
            If fails: print a error message and returns False
            If succeed: OrderedDict: A dict containing
                ('SchemasName' : schema_obj) pairs
    """

    if os.path.isdir(schema_dir) is False:
        logging.error("Schema dir is not a valid dir: {}".format(schema_dir))
        return None
    if os.access(schema_dir, os.R_OK) is False:
        logging.error("Can't access dir {}".format(schema_dir))
        return None

    schema_dict = collections.OrderedDict()
    for key in schemas:
        try:
            with open(schema_dir + '/' + schemas[key]) as f:
                schema_dict[key] = json.load(f)
        except Exception as e:
            logging.error(e)
            return None
    return schema_dict