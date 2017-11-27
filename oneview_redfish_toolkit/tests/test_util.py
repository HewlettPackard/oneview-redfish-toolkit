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
import configparser
import os
import socket

from oneview_redfish_toolkit.api import errors
from oneview_redfish_toolkit import util
import unittest
from unittest import mock


class TestUtil(unittest.TestCase):
    """Test class for util

        Tests:
            load_conf()
                - invalid ini file
                - valid ini file
                - have all expected sessions
                - have all expected options
            load_schema()
                - invalid schema dir
                - valid schema dir invalid schemas dict
                - valid schema dir and dict

            get_oneview_client()
                - connection recover
                - connection renew
                - connection failure


            load_config()
                - checkes if globals vars are not none
    """

    # load_conf() tests
    def setUp(self):
        self.schema_dir = './oneview_redfish_toolkit/schemas'
        self.registry_dir = './oneview_redfish_toolkit/registry'
        self.config_file = './redfish.conf'

    def test_load_conf_invalid_config_file(self):
        # Tests if passing a file that does not exists returns false.
        try:
            util.load_conf('non-exist.conf')
        except Exception as e:
            self.assertIsInstance(
                e,
                errors.OneViewRedfishResourceNotFoundError
            )

    def test_load_conf_valid_config_file(self):
        # Tests if passing a valid file returns a object
        self.assertIsInstance(util.load_conf(self.config_file),
                              configparser.ConfigParser)

    def test_load_conf_has_all_expect_sessions(self):
        # Tests if ini file has all expected sections
        cfg = util.load_conf(self.config_file)

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
        self.assertTrue(cfg.has_section('registry'),
                        msg='Section {} not found in ini file {}'.
                        format('registry', self.config_file))

    def test_load_conf_has_all_options(self):
        # Tests if ini file has all expected options

        cfg = util.load_conf(self.config_file)

        self.assertTrue(cfg.has_option('redfish', 'schema_dir'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('schema_dir', 'redfish',
                        self.config_file))
        self.assertTrue(cfg.has_option('redfish', 'indent_json'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('indent_json', 'redfish',
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
        except Exception as e:
            self.assertIsInstance(
                e,
                errors.OneViewRedfishResourceNotFoundError,
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
                errors.OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    def test_load_schemas_valid_schema_dir_valid_dict(self):
        # Tests loading schemas files from redfish.conf

        cfg = util.load_conf(self.config_file)
        schemas = dict(cfg.items('schemas'))

        try:
            schemas_dict = util.load_schemas(self.schema_dir, schemas)
            self.assertIsInstance(schemas_dict, collections.OrderedDict)
        except Exception as e:
            self.fail('Failed to load schemas files: {}'.format(e.msg))

    # load_schemas() tests
    def test_load_registries_invalid_registry_dir(self):
        # Tests load_registry() passing a non existing registry dir

        schemas = dict()

        try:
            util.load_schemas('non-exist-registry-dir', schemas)
        except Exception as e:
            self.assertIsInstance(
                e,
                errors.OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    def test_load_registries_valid_registry_dir_invalid_dict(self):
        # Tests load_registry() passing a valid registry dir and an invalid
        # registry dict

        registries = dict()
        registries['failed'] = 'fail.json'

        try:
            util.load_registry(self.registry_dir, registries)
        except Exception as e:
            self.assertIsInstance(
                e,
                errors.OneViewRedfishResourceNotFoundError,
                msg="Unexpected exception: {}".format(e.msg)
            )

    def test_load_registries_valid_registry_dir_valid_dict(self):
        # Tests loading regitry files from redfish.conf

        cfg = util.load_conf(self.config_file)
        registries = dict(cfg.items('registry'))

        try:
            registry_dict = util.load_schemas(self.registry_dir, registries)
            self.assertIsInstance(registry_dict, collections.OrderedDict)
        except Exception as e:
            self.fail('Failed to load registries files: {}'.format(e.msg))

    @mock.patch.object(util, 'OneViewClient')
    def test_load_config(self, mock_ov):
        # Teste load config function

        util.load_config(self.config_file)

        # After running loadconfig all variable should be set
        self.assertIsNotNone(util.config, msg='Failed do load ini')
        self.assertIsNotNone(util.ov_config, msg='Failed do create ov_config')
        self.assertIsNotNone(util.schemas_dict, msg='Failed to load schemas')
        self.assertIsNotNone(
            util.registry_dict,
            msg='Failed to load registries')
        self.assertIsNotNone(util.ov_client, msg='Failed to connect to OV')

    @mock.patch.object(util, 'OneViewClient')
    def test_get_ov_client_recover(self, oneview_client_mockup):
        # Tests a successful recover of a OV client

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get.return_value = list()

        try:
            ov_client = util.OneViewClient()
        except Exception as e:
            self.fail('Failed to connect to OneView: '.format(e))
        self.assertIsNotNone(ov_client)

    @mock.patch.object(util, 'OneViewClient')
    def test_get_ov_client_renew(self, oneview_client_mockup):
        """Tests getting a OV client from expired session"""

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get.return_value = \
            Exception('session expired')
        oneview_client.connection.login.return_value = oneview_client

        try:
            ov_client = util.OneViewClient()
        except Exception as e:
            self.fail('Failed to connect to OneView: '.format(e))
        self.assertIsNotNone(ov_client)

    @mock.patch.object(util, 'OneViewClient')
    def test_get_ov_client_oneview_offline(self, oneview_client_mockup):
        """Tests getting a OV client from an offline oneview"""

        oneview_client = oneview_client_mockup()
        oneview_client.connection.get.return_value = \
            Exception('OneView not responding')
        oneview_client.connection.login.return_value = \
            Exception('OneView not responding')

        try:
            ov_client = util.OneViewClient()
        except Exception as e:
            self.fail('Failed to connect to OneView: '.format(e))
        self.assertIsNotNone(ov_client)

    def test_get_ip(self):
        # Tests get_ip function; This test may not work if it returns an IPV6.
        ip = util.get_ip()
        try:
            socket.inet_aton(ip)
        except Exception:
            self.fail("Failed to get a valid IP Address")

    @mock.patch.object(util, 'OneViewClient')
    def test_creat_certs(self, oneview_client_mockup):
        # Test generate_certificate function

        util.load_config(self.config_file)

        util.generate_certificate("certs", "test", 2048)

        self.assertTrue(os.path.exists(os.path.join("certs", "test" + ".crt")))
        self.assertTrue(os.path.exists(os.path.join("certs", "test" + ".key")))
