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

"""
    Tests for load_schema and load_registry function from util.py
"""

import collections
import configparser

from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api import schemas
from oneview_redfish_toolkit import config
import unittest


class TestUtil(unittest.TestCase):
    """Test class for config

        Tests:
            load_conf_file()
                - invalid ini file
                - valid ini file
                - have all expected sessions
                - have all expected options
                - checks if globals vars are not none

            load_schema()
                - invalid schema dir

            load_registry()
                - invalid schema dir
                - valid schema dir invalid schemas dict
                - valid schema dir and dict

    """

    # load_conf_file() tests
    def setUp(self):
        self.schema_dir = './oneview_redfish_toolkit/schemas'
        self.registry_dir = './oneview_redfish_toolkit/registry'
        self.config_file = './oneview_redfish_toolkit/conf/redfish.conf'

    def test_load_conf_invalid_config_file(self):
        # Tests if passing a file that does not exists returns false.
        try:
            config.load_conf_file('non-exist.conf')
        except Exception as e:
            self.assertIsInstance(
                e,
                OneViewRedfishResourceNotFoundError
            )

    def test_load_conf_valid_config_file(self):
        # Tests if passing a valid file returns a object
        self.assertIsInstance(config.load_conf_file(self.config_file),
                              configparser.ConfigParser)

    def test_load_conf_has_all_expect_sessions(self):
        # Tests if ini file has all expected sections
        cfg = config.load_conf_file(self.config_file)

        self.assertTrue(cfg.has_section('redfish'),
                        msg='Section {} not found in ini file {}'.format(
                        'redfish', self.config_file))
        self.assertTrue(cfg.has_section('oneview_config'),
                        msg='Section {} not found in ini file {}'.
                        format('oneview_config', self.config_file))
        self.assertTrue(cfg.has_section('credentials'),
                        msg='Section {} not found in ini file {}'.
                        format('credentials', self.config_file))
        self.assertTrue(cfg.has_section('event_service'),
                        msg='Section {} not found in ini file {}'.
                        format('event_service', self.config_file))

    def test_load_conf_has_all_options(self):
        # Tests if ini file has all expected options

        cfg = config.load_conf_file(self.config_file)

        self.assertTrue(cfg.has_option('redfish', 'indent_json'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('indent_json', 'redfish',
                        self.config_file))
        self.assertTrue(cfg.has_option('oneview_config', 'ip'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('ip', 'oneview_config', self.config_file))
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

        try:
            config.load_schemas('non-exist-schema-dir')
        except Exception as e:
            self.assertIsInstance(
                e,
                OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    # load_registry() tests
    def test_load_registries_invalid_registry_dir(self):
        # Tests load_registry() passing a non existing registry dir

        schemas = dict()

        try:
            config.load_registry('non-exist-registry-dir', schemas)
        except Exception as e:
            self.assertIsInstance(
                e,
                OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    def test_load_registries_valid_registry_dir_invalid_dict(self):
        # Tests load_registry() passing a valid registry dir and an invalid
        # registry dict

        registries = dict()
        registries['failed'] = 'fail.json'

        try:
            config.load_registry(self.registry_dir, registries)
        except Exception as e:
            self.assertIsInstance(
                e,
                OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    def test_load_registries_valid_registry_dir_valid_dict(self):
        # Tests loading registry files from redfish.conf

        registries = schemas.REGISTRY

        try:
            registry_dict = config.load_registry(self.registry_dir, registries)
            self.assertIsInstance(registry_dict, collections.OrderedDict)
        except Exception as e:
            self.fail('Failed to load registries files: {}'.format(e.msg))
