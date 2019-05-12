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
import json
import logging
import os
import pika
import ssl
from threading import Thread

# 3rd party libs
from hpOneView.exceptions import HPOneViewException
from hpOneView.resources.resource import ResourceClient
from pika.credentials import ExternalCredentials

# Own libs
from oneview_redfish_toolkit.api.errors import NOT_FOUND_ONEVIEW_ERRORS
from oneview_redfish_toolkit.api.errors import OneViewRedfishException
from oneview_redfish_toolkit.api.event import Event
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit import util

SCMB_DIR_NAME = "scmb"
ONEVIEW_CA_NAME = "oneview_ca.pem"
SCMB_CERT_NAME = "oneview_scmb.pem"
SCMB_KEY_NAME = "oneview_scmb.key"
SCMB_PORT = 5671
SCMB_SOCKET_TIMEOUT = 5  # seconds
SCMB_RESOURCE_LIST = [
    'alerts',
    'enclosures',
    'racks',
    'server-hardware']
SCMB_EXCHANGE_NAME = 'scmb'


def init_map_scmb_connections():
    globals()['map_scmb_connections'] = []


def _get_map_scmb_connections():
    return globals()['map_scmb_connections']


def _set_map_scmb_connections(ov_ip):
    globals()['map_scmb_connections'].append(ov_ip)


def _scmb_base_dir():
    certs_dir = os.path.dirname(config.get_config()['ssl']['SSLCertFile'])
    return os.path.join(certs_dir, SCMB_DIR_NAME)


def _scmb_oneview_dir(ov_ip):
    return os.path.join(_scmb_base_dir(), ov_ip)


def _oneview_ca_path(ov_ip):
    return os.path.join(_scmb_oneview_dir(ov_ip), ONEVIEW_CA_NAME)


def _scmb_cert_path(ov_ip):
    return os.path.join(_scmb_oneview_dir(ov_ip), SCMB_CERT_NAME)


def _scmb_key_path(ov_ip):
    return os.path.join(_scmb_oneview_dir(ov_ip), SCMB_KEY_NAME)


def init_event_service(token=None):
    # Iterate through each ov and fork a new thread to listen scmb
    list_ov_ips = config.get_oneview_multiple_ips()

    for ov_ip in list_ov_ips:
        # Loading scmb connection
        # If scmb connection is already present for respective ov then
        # do not fork new thread to listen scmb
        if ov_ip not in _get_map_scmb_connections():
            scmb_thread = SCMB(ov_ip, config.get_credentials(), token)
            scmb_thread.daemon = True
            scmb_thread.start()


class SCMB(Thread):
    def __init__(self, ov_ip, cred, token):
        Thread.__init__(self)
        self.ov_ip = ov_ip
        self.cred = cred
        self.token = token

    def run(self):
        if self._has_valid_certificates():
            logging.info('SCMB certs already exist and are valid...')
        else:
            logging.info('SCMB certs not found. '
                         'Checking if already generated in Oneview...')
            self.get_scmb_certs()
            logging.info('Got certs. Testing connection...')
            if not self._is_cert_working_with_scmb():
                logging.error('Failed to connect to scmb. Aborting...')
                exit(1)

        self._listen_scmb()

    def _has_valid_certificates(self):
        try:
            return self._has_scmb_certificates_path() and \
                self._is_cert_working_with_scmb()
        except KeyError as error:
            logging.error("Invalid configuration for ssl cert. "
                          "Verify the [ssl] section in config file")
            raise error

    def _has_scmb_certificates_path(self):
        return os.path.isfile(_oneview_ca_path(self.ov_ip)) and \
            os.path.isfile(_scmb_cert_path(self.ov_ip)) and \
            os.path.isfile(_scmb_key_path(self.ov_ip))

    def _get_ov_ca_cert(self, ov_client):
        URI = '/rest/certificates/ca'
        resource_client = ResourceClient(ov_client.connection, URI)
        cert = resource_client.get(URI + "?filter=certType:INTERNAL")
        return cert

    def _get_ov_ca_cert_base64data(self, ov_client):
        cert = self._get_ov_ca_cert(ov_client)
        returnCert = None
        if isinstance(cert, dict):
            if 'members' in cert.keys():
                for certObj in cert.get('members'):
                    if certObj and certObj.get('certificateDetails') and \
                            certObj.get('certificateDetails'). \
                            get('base64Data'):
                        returnCert = certObj.get('certificateDetails').\
                            get('base64Data')
                        break
            return returnCert
        # If cert is not a dictionary then returning None
        return returnCert

    def get_scmb_certs(self):
        # Get CA
        ov_client = client_session.get_oneview_client(self.ov_ip, self.token)

        cert = self._get_ov_ca_cert_base64data(ov_client)

        if cert is None:
            raise OneViewRedfishException(
                "Failed to fetch OneView CA Certificate"
            )

        # Create the base scmb dir to save the scmb files
        os.makedirs(name=_scmb_base_dir(), exist_ok=True)

        # Create the dir to save the scmb files for respective ov
        os.makedirs(name=_scmb_oneview_dir(self.ov_ip), exist_ok=True)

        with open(_oneview_ca_path(self.ov_ip), 'w+') as f:
            f.write(cert)

        certs = self._get_scmb_certificate_from_ov(ov_client)

        # Save cert
        with open(_scmb_cert_path(self.ov_ip), 'w+') as f:
            f.write(certs['base64SSLCertData'])

        # Save key
        with open(_scmb_key_path(self.ov_ip), 'w+') as f:
            f.write(certs['base64SSLKeyData'])

    def _generate_certificate_in_oneview(self, ov_client):
        try:
            cert_info = {
                "commonName": "default",
                "type": "RabbitMqClientCertV2"
            }
            ov_client.certificate_rabbitmq.generate(cert_info)
        except HPOneViewException as e:
            # Cert with that commonName already exists. We are going to get it
            if e.oneview_response["errorCode"] == 'RABBITMQ_CLIENTCERT_' \
                                                  'CONFLICT':
                logging.info('Certs already exists in oneview')
            else:
                # Another error is not expected, we raise.
                logging.exception("Unexpected error")
                raise e

    def _get_scmb_certificate_from_ov(self, ov_client):
        cert = None
        try:
            cert = ov_client.certificate_rabbitmq.get_key_pair('default')
            logging.info('SCMB certs retrieved from OneView.')
        except HPOneViewException as e:
            if e.oneview_response["errorCode"] in NOT_FOUND_ONEVIEW_ERRORS:
                logging.info('Generating SCMB cert in Oneview...')
                self._generate_certificate_in_oneview(ov_client)
                cert = ov_client.certificate_rabbitmq.get_key_pair('default')
            else:
                logging.exception("Unexpected error")
                raise e
        return cert

    def scmb_connect(self):
        scmb_server = self.ov_ip

        # Setup our ssl options
        ssl_options = ({'ca_certs': _oneview_ca_path(self.ov_ip),
                        'certfile': _scmb_cert_path(self.ov_ip),
                        'keyfile': _scmb_key_path(self.ov_ip),
                        'cert_reqs': ssl.CERT_REQUIRED,
                        'server_side': False})

        scmb_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                scmb_server,
                SCMB_PORT,
                credentials=ExternalCredentials(),
                socket_timeout=SCMB_SOCKET_TIMEOUT,
                ssl=True,
                ssl_options=ssl_options))

        return scmb_connection

    def _is_cert_working_with_scmb(self):
        # Create and bind to queue
        EXCHANGE_NAME = 'scmb'
        ROUTE = 'scmb.alerts.#'
        try:
            scmb_conn = self.scmb_connect()
            channel = scmb_conn.channel()
            queue = channel.queue_declare(auto_delete=True)
            channel.queue_bind(
                queue=queue.method.queue,
                exchange=EXCHANGE_NAME,
                routing_key=ROUTE)
            channel.close()
            scmb_conn.close()
        except Exception:
            logging.exception("Failed to test scmb connection")
            return False
        return True

    def consume_message(self, ch, method, properties, body):
        body = json.loads(body.decode('utf-8'))
        resource = body['resource']

        if (resource['category'] == 'alerts'):
            category = resource['associatedResource']['resourceCategory']
        else:
            category = resource['category']

        if (category in SCMB_RESOURCE_LIST):
            event = Event(body)

            util.dispatch_event(event)
        else:
            logging.debug('SCMB message received for an unmanaged resource')

    def _listen_scmb(self):
        try:
            scmb_conn = self.scmb_connect()
            ch = scmb_conn.channel()

            queue_name = ch.queue_declare(auto_delete=True)

            for resource in SCMB_RESOURCE_LIST:
                # scmb.<resource>.#
                route = SCMB_EXCHANGE_NAME + '.' + resource + '.#'

                ch.queue_bind(
                    queue=queue_name.method.queue,
                    exchange=SCMB_EXCHANGE_NAME,
                    routing_key=route)

            ch.basic_consume(self.consume_message,
                             queue=queue_name.method.queue)
            ch.start_consuming()

            # Make scmb enabled flag true for current ov
            _set_map_scmb_connections(self.ov_ip)
        except KeyboardInterrupt:
            ch.close()
            scmb_conn.close()
        except Exception:
            logging.exception("Failed to listen to scmb messages")
