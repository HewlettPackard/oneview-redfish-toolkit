# -*- coding: utf-8 -*-

# Copyright (2017-2018) Hewlett Packard Enterprise Development LP
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
import os
import shutil
from unittest import mock

# 3rd party libs
from hpOneView.exceptions import HPOneViewException

# Own libs
from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.tests.base_test import BaseTest
from oneview_redfish_toolkit import util


class TestSCMB(BaseTest):
    """Tests for SCMB module"""

    @mock.patch.object(scmb, '_is_cert_working_with_scmb')
    @mock.patch.object(scmb, 'config')
    @mock.patch('os.path.isfile')
    def test_check_cert_exist(self, isfile, config_mock,
                              _is_cert_working_with_scmb):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': ''
            }
        }

        # Files exist
        isfile.return_value = True
        _is_cert_working_with_scmb.return_value = True
        self.assertTrue(scmb._has_valid_certificates())

        # Certs files don't exist
        isfile.return_value = False
        _is_cert_working_with_scmb.return_value = False
        self.assertFalse(scmb._has_valid_certificates())
        self.assertFalse(scmb._has_valid_certificates())

    @mock.patch.object(scmb, 'config')
    def test_paths_generated_for_scmb_files(self, config_mock):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': '/dir/cert_file.crt'
            }
        }

        self.assertEqual('/dir/scmb/oneview_ca.pem', scmb._oneview_ca_path())
        self.assertEqual('/dir/scmb/oneview_scmb.pem', scmb._scmb_cert_path())
        self.assertEqual('/dir/scmb/oneview_scmb.key', scmb._scmb_key_path())

    @mock.patch.object(scmb, 'config')
    @mock.patch.object(scmb, 'logging')
    def test_check_cert_exist_when_config_key_is_missing(self,
                                                         logging_mock,
                                                         config_mock):
        config_mock.get_config.return_value = {
            'ssl': {}
        }

        with self.assertRaises(KeyError) as error:
            scmb._has_valid_certificates()

        logging_mock.error.assert_called_with(
            'Invalid configuration for ssl cert. '
            'Verify the [ssl] section in config file')

        self.assertEqual("'SSLCertFile'", str(error.exception))

    @mock.patch.object(scmb, '_is_cert_working_with_scmb')
    @mock.patch.object(scmb, 'config')
    @mock.patch.object(scmb, 'get_oneview_client')
    def test_get_cert_already_exists(self, get_oneview_client, config_mock,
                                     _is_cert_working_with_scmb):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': 'cert_file.crt'
            }
        }

        os.makedirs(name='scmb', exist_ok=True)
        self.addCleanup(shutil.rmtree, 'scmb')

        # Certs Generated with success
        oneview_client = mock.MagicMock()
        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        oneview_client.certificate_rabbitmq.get_key_pair.return_value = {
            'base64SSLCertData': 'Client CERT',
            'base64SSLKeyData': 'Client Key'}
        get_oneview_client.return_value = oneview_client
        _is_cert_working_with_scmb.return_value = True

        # Certs already exist
        e = HPOneViewException({
            'errorCode': 'RABBITMQ_CLIENTCERT_CONFLICT',
            'message': 'certs already exist',
        })
        oneview_client.certificate_rabbitmq.generate.side_effect = e
        scmb.get_cert()
        self.assertTrue(scmb._has_valid_certificates())

    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch('pika.credentials.ExternalCredentials')
    def test_scmb_connect(self, blk_conn, conn_params, ext_cred):
        blk_conn.return_value = {}
        conn_params.return_value = {}
        ext_cred.return_value = {}
        self.assertEqual(scmb.scmb_connect(), {})

    @mock.patch.object(util, 'dispatch_event')
    def test_consume_message(self, dispatch_mock):
        with open(
            'oneview_redfish_toolkit/mockups/oneview/Alert.json'
        ) as f:
            event_mockup = f.read().encode('UTF-8')

        scmb.consume_message(None, None, None, event_mockup)

        self.assertTrue(dispatch_mock.called)

    @mock.patch.object(scmb, 'config')
    @mock.patch.object(scmb, '_is_cert_working_with_scmb')
    @mock.patch.object(scmb, 'get_oneview_client')
    def test_generate_new_cert_for_oneview(self, get_oneview_client,
                                           _is_cert_working_with_scmb,
                                           config_mock):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': 'cert_file.crt'
            }
        }

        cert_key_pair = {
            'base64SSLCertData': 'Client CERT',
            'base64SSLKeyData': 'Client Key'
        }

        # Certs Generated with success
        oneview_client = mock.MagicMock()
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'Resource not found.',
        })

        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        oneview_client.certificate_rabbitmq.get_key_pair.side_effect = \
            [e, cert_key_pair]
        get_oneview_client.return_value = oneview_client
        _is_cert_working_with_scmb.return_value = True
        scmb.get_cert()
        self.assertTrue(scmb._has_valid_certificates())

    @mock.patch.object(scmb, 'config')
    @mock.patch.object(scmb, 'get_oneview_client')
    def test_get_oneview_cert_unexpected_error(self, get_oneview_client,
                                               config_mock):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': 'cert_file.crt'
            }
        }

        # Certs Generated with success
        oneview_client = mock.MagicMock()
        e = HPOneViewException({
            'errorCode': 'UNEXPECTED ERROR',
            'message': 'Unexpected error.',
        })
        hp_ov_exception_msg = "Unexpected error."

        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        oneview_client.certificate_rabbitmq.get_key_pair.side_effect = e
        get_oneview_client.return_value = oneview_client

        with self.assertRaises(HPOneViewException) as hp_exception:
            scmb.get_cert()

        test_exception = hp_exception.exception
        self.assertEqual(hp_ov_exception_msg, test_exception.msg)
        self.assertEqual(e.oneview_response, test_exception.oneview_response)

    @mock.patch('pika.channel.Channel')
    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch.object(scmb, 'config')
    @mock.patch.object(scmb, 'get_oneview_client')
    def test_init_event_service_with_valid_certificate(self,
                                                       get_oneview_client,
                                                       config_mock, conn_param,
                                                       block_conn, channel):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': 'cert_file.crt'
            },
        }

        os.makedirs(name='scmb', exist_ok=True)
        self.addCleanup(shutil.rmtree, 'scmb')

        oneview_client = mock.MagicMock()
        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        get_oneview_client.return_value = oneview_client
        oneview_client.certificate_rabbitmq.get_key_pair.return_value = {
            'base64SSLCertData': 'Client CERT',
            'base64SSLKeyData': 'Client Key'}

        pika_mock = mock.MagicMock()
        pika_mock.channel.Channel = {}
        block_conn.return_value = pika_mock
        conn_param.return_value = {}
        channel.return_value = {}

        scmb.init_event_service()

        self.assertTrue(scmb._has_valid_certificates())
        self.assertTrue(scmb._is_cert_working_with_scmb())

    @mock.patch.object(config, 'config')
    def test_init_event_service_on_session_mode(self, config_mock):
        config_mock.get_authentication_mode.return_value = 'session'
        scmb.init_event_service()

        self.assertFalse(scmb._has_valid_certificates())
        self.assertFalse(scmb._is_cert_working_with_scmb())

    @mock.patch('pika.channel.Channel')
    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch.object(scmb, '_has_scmb_certificates_path')
    @mock.patch.object(scmb, 'get_oneview_client')
    @mock.patch.object(scmb, 'config')
    def test_init_event_service_with_certs_already_generated(self, config_mock,
                                                             get_ov_client,
                                                             _has_certs_path,
                                                             conn_param,
                                                             block_conn,
                                                             channel):
        config_mock.get_config.return_value = {
            'ssl': {
                'SSLCertFile': '/dir/cert_file.crt'
            },
        }

        pika_mock = mock.MagicMock()
        pika_mock.channel.Channel = {}
        block_conn.return_value = pika_mock
        conn_param.return_value = {}
        channel.return_value = {}
        oneview_client = mock.MagicMock()
        get_ov_client.return_value = oneview_client
        _has_certs_path.return_value = True

        scmb.init_event_service()

        self.assertTrue(scmb._has_valid_certificates())
