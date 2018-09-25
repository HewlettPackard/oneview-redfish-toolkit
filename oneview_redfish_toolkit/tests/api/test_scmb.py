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

from unittest import mock

from hpOneView.exceptions import HPOneViewException

from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit.tests.base_test import BaseTest
from oneview_redfish_toolkit import util


class TestSCMB(BaseTest):
    """Tests for SCMB module"""

    @mock.patch.object(scmb, 'is_cert_working_with_scmb')
    @mock.patch('os.path.isfile')
    def test_check_cert_exist(self, isfile, is_cert_working_with_scmb):
        # Files exist and cert is working with scmb
        isfile.return_value = True
        is_cert_working_with_scmb.return_value = True
        scmb.is_cert_working_with_scmb.return_value = True
        self.assertTrue(scmb.has_valid_certificate())

        # Certs files does not exist
        isfile.return_value = False
        self.assertFalse(scmb.has_valid_certificate())

        # Certs exist but is not working with scmb
        isfile.return_value = True
        is_cert_working_with_scmb.return_value = True
        scmb.is_cert_working_with_scmb.return_value = False
        self.assertFalse(scmb.has_valid_certificate())

    @mock.patch.object(scmb, 'is_cert_working_with_scmb')
    @mock.patch.object(scmb, 'get_oneview_client')
    def test_get_cert_already_exists(self, get_oneview_client,
                                     is_cert_working_with_scmb):
        # Certs Generated with success
        oneview_client = mock.MagicMock()
        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        oneview_client.certificate_rabbitmq.get_key_pair.return_value = {
            'base64SSLCertData': 'Client CERT',
            'base64SSLKeyData': 'Client Key'}
        get_oneview_client.return_value = oneview_client
        is_cert_working_with_scmb.return_value = True
        scmb.get_cert()
        self.assertTrue(scmb.has_valid_certificate())
        # Certs already exist
        e = HPOneViewException({
            'errorCode': 'RABBITMQ_CLIENTCERT_CONFLICT',
            'message': 'certs already exist',
        })
        oneview_client.certificate_rabbitmq.generate.side_effect = e
        scmb.get_cert()
        self.assertTrue(scmb.has_valid_certificate())

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

    @mock.patch.object(scmb, 'is_cert_working_with_scmb')
    @mock.patch.object(scmb, 'get_oneview_client')
    def test_generate_new_scmb_cert(self, get_oneview_client,
                                    is_cert_working_with_scmb):
        # Certs Generated with success
        oneview_client = mock.MagicMock()
        e = HPOneViewException({
            'errorCode': 'RESOURCE_NOT_FOUND',
            'message': 'Resource not found.',
        })
        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        oneview_client.certificate_rabbitmq.get_key_pair.side_effect = e
        get_oneview_client.return_value = oneview_client
        is_cert_working_with_scmb.return_value = True
        scmb.get_cert()
        self.assertTrue(scmb.has_valid_certificate())
