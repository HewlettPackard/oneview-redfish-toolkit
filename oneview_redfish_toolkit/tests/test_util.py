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

"""
    Tests for load_schemas function from util.py
"""

import collections
from oneview_redfish_toolkit import util
from oneview_redfish_toolkit.error import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.error import\
    OneViewRedfishResourceNotFoundAccessible
import unittest


class TestUtil(unittest.TestCase):
    '''Test class for util

        Tests:
            load_ini()
                - invalid ini file
                - valid ini file
                - have all expected sessions
                - have all exepect options
            load_schema()
                - invalid schema dir
                - valid schema dir invalid schemas dict
                - valid schema dir and dict

            get_oneview_client()
                - invalid credentials
                - valid credentials

            load_config()
                - checkes if globals vars are not none



    '''

    # load_ini() tests
    def setUp(self):
        self.schema_dir = './oneview_redfish_toolkit/schemas'
        self.config_file = './oneview_redfish_toolkit/redfish.ini'

    def test_load_ini_invalid_config_file(self):
        # Tests if passing a file that does not exists returns false.
        try:
            util.load_ini('non-exist.ini')
        except Exception as e:
            assertIsInstance(e, OneViewRedfishResourceNotFoundError)

    def test_load_ini_valid_config_file(self):
        # Tests if passing a valid file returns a object
        self.assertIsInstance(util.load_ini(self.config_file),
                              configparser.ConfigParser)

    def test_load_ini_has_all_expect_sessions(self):
        # Tests if ini file has all expected sections
        cfg = util.load_ini(self.config_file)

        self.assertTrue(cfg.has_section('redfish'),
                        msg='Section {} not found in ini file {}'.format(
                        'redfish', self.config_file))
        self.assertTrue(cfg.has_section('oneview_config'),
                        msg='Section {} not found in ini file {}'.
                        format('oneview_config', self.config_file))
        self.assertTrue(cfg.has_section('credentials'),
                        msg='Section {} not found in ini file {}'.
                        format('credentials', self.config_file))
        self.assertTrue(cfg.has_section('schemas'),
                        msg='Section {} not found in ini file {}'.
                        format('schemas', self.config_file))

    def test_load_ini_has_all_options(self):
        # Tests if ini file has all expected options

        cfg = util.load_ini(self.config_file)

        self.assertTrue(cfg.has_option('redfish', 'schema_dir'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('schema_dir', 'redfish',
                        self.config_file))
        self.assertTrue(cfg.has_option('redfish', 'ident_json'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('ident_json', 'redfish',
                        self.config_file))
        self.assertTrue(cfg.has_option('redfish', 'log_file'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('log_file', 'redfish',
                        self.config_file))
        self.assertTrue(cfg.has_option('oneview_config', 'ip'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('ip', 'oneview_config', self.config_file))
        self.assertTrue(cfg.has_option('oneview_config', 'api_version'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('schema_dir', 'oneview_config',
                        self.config_file))
        self.assertTrue(cfg.has_option('credentials', 'userName'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('userName', 'credentials',
                        self.config_file))
        self.assertTrue(cfg.has_option('credentials', 'password'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('password', 'credentials',
                        self.config_file))

    # load_schemas() tests
    def test_load_schemas_invalid_schema_dir(self):
        # Tests if passing a non existing schema dir returns False

        schemas = dict()

        try:
            util.load_schemas('non-exist-schema-dir', schemas)
        except Exception e:
            self.assertIsInstance(e,
                OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )


    def test_load_schemas_valid_schema_dir_invalid_dict(self):
        # Tests if passing a valid schema dir and an invalid schema dict
        # returns False

        schemas = dict()
        schemas['failed'] = 'fail.json'

        try:
            util.load_schemas(self.schema_dir, schemas)
        except Exception as e:
            self.assertIsInstance(
                e,
                OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    def test_load_schemas_valid_schema_dir_valid_dict(self):
        # Tests if ini file has all expected sections

        cfg = util.load_config(self.config_file)
        schemas = dict(cfg.items('schemas'))

        try:
            schemas_dict = util.load_schemas(self.schema_dir, schemas)
            self.assertIsInstance(schemas_dict, collections.OrderedDict)
        except Exception as e:
            self.fail('Failed to load schemas files: {}'.format(e.msg))
