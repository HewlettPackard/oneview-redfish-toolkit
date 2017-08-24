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
    Tests for load_config function from util.py
"""

import configparser
import unittest

from oneview_redfish_toolkit import util


class TestUtilLoadConfig(unittest.TestCase):

    def setUp(self):
        self.config_file = './oneview_redfish_toolkit/redfish.ini'

    def test_invalid_config_file(self):
        # Tests if passing a file that does not exists returns false.
        self.assertFalse(util.load_config('non-exist.ini'))

    def test_valid_config_file(self):
        # Tests if passing a valid file returns a object

        self.assertIsInstance(util.load_config(self.config_file),
                              configparser.ConfigParser)

    def test_has_all_expect_sessions(self):
        # Tests if ini file has all expected sections

        cfg = util.load_config(self.config_file)

        self.assertTrue(cfg.has_section('directories'),
                        msg='Section {} not found in ini file {}'.format(
                        'directories', self.config_file))
        self.assertTrue(cfg.has_section('oneview_config'),
                        msg='Section {} not found in ini file {}'.
                        format('oneview_config', self.config_file))
        self.assertTrue(cfg.has_section('credentials'),
                        msg='Section {} not found in ini file {}'.
                        format('credentials', self.config_file))
        self.assertTrue(cfg.has_section('schemas'),
                        msg='Section {} not found in ini file {}'.
                        format('schemas', self.config_file))

    def test_has_all_options(self):
        # Tests if ini file has all expected options

        cfg = util.load_config(self.config_file)

        self.assertTrue(cfg.has_option('directories', 'schema_dir'),
                        msg='Option {} not found in section {} in ini file {}'
                        .format('schema_dir', 'directories',
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
