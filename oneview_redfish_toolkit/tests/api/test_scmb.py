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

from contextlib import contextmanager
from io import StringIO
import sys
import unittest
from unittest import mock

from hpOneView.exceptions import HPOneViewException

from oneview_redfish_toolkit.api import scmb
from oneview_redfish_toolkit import util


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestSCMB(unittest.TestCase):
    """Tests for Chassis class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mock):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

    @mock.patch('os.path.isfile')
    def test_check_cert_exist(self, isfile):
        # Files exist
        isfile.return_value = True
        self.assertTrue(scmb.check_cert_exist())
        # Certs files don't exist
        isfile.return_value = False
        self.assertFalse(scmb.check_cert_exist())

    @mock.patch.object(util, 'ov_client')
    def test_get_cert(self, oneview_client):
        # Certs Generated with success
        oneview_client.certificate_authority.get.return_value = "CA CERT"
        oneview_client.certificate_rabbitmq.generate.return_value = True
        oneview_client.certificate_rabbitmq.get_key_pair.return_value = {
            'base64SSLCertData': 'Client CERT',
            'base64SSLKeyData': 'Client Key'}
        scmb.get_cert()
        self.assertTrue(scmb.check_cert_exist())
        # Certs already exist
        e = HPOneViewException({
            'errorCode': 'RABBITMQ_CLIENTCERT_CONFLICT',
            'message': 'certs already exist',
        })
        oneview_client.certificate_rabbitmq.generate.side_effect = e
        scmb.get_cert()
        self.assertTrue(scmb.check_cert_exist())

    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch('pika.credentials.ExternalCredentials')
    def test_scmb_connect(self, blk_conn, conn_params, ext_cred):
        blk_conn.return_value = {}
        conn_params.return_value = {}
        ext_cred.return_value = {}
        self.assertEqual(scmb.scmb_connect(), {})

    def test_consume_message(self):
        with captured_output() as (out, err):
            scmb.consume_message(None, None, None, b'{"teste": "teste"}')
            output = out.getvalue().strip()
            self.assertEqual(output, '{\n    "teste": "teste"\n}')
