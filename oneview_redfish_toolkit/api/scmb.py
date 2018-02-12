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

import logging
import json
import os
import ssl
import sys

import pika
from pika.credentials import ExternalCredentials
from hpOneView.exceptions import HPOneViewException


from oneview_redfish_toolkit import util


ONEVIEW_CA = "certs/oneview_ca.pem"
SCMB_CERT = "certs/oneview_scmb.pem"
SCMB_KEY = "certs/oneview_scmb.key"


def check_cert_exist():
    if not os.path.isfile(ONEVIEW_CA):
        return False
    if not os.path.isfile(SCMB_CERT):
        return False
    if not os.path.isfile(SCMB_KEY):
        return False
    return True

def get_cert():
    # Get CA
    cert = util.ov_client.certificate_authority.get()
    with open(util.config['scmb']['oneview_ca'], 'w+') as f:
        f.write(cert)
    # Generate scmb Cert:
    try:
        cert_info = {
            "commonName": "default",
            "type": "RabbitMqClientCertV2"
        }
        util.ov_client.certificate_rabbitmq.generate(cert_info)
    except HPOneViewException as e:
        print(dir(e.oneview_response))
        # Cert with that commonName already exists. We are going to get it
        if e.oneview_response["errorCode"] == 'RABBITMQ_CLIENTCERT_CONFLICT':
            logging.info('Certs already exists in oneview')
        else:
            # Another error is not expected, we raise.
            raise
    # Get the scmb certs key pair
    certs = util.ov_client.certificate_rabbitmq.get_key_pair(
        'default')
    # Save cert
    with open(util.config['scmb']['scmb_cert'], 'w+') as f:
        f.write(certs['base64SSLCertData'])
    # Save key
    with open(util.config['scmb']['scmb_key'], 'w+') as f:
        f.write(certs['base64SSLKeyData'])


def scmb_connect():
    scmb_server = util.config['oneview_config']['ip']

    # Setup our ssl options
    ssl_options = ({'ca_certs': ONEVIEW_CA,
                    'certfile': SCMB_CERT,
                    'keyfile': SCMB_KEY,
                    'cert_reqs': ssl.CERT_REQUIRED,
                    'server_side': False})

    scmb_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
        scmb_server, 5671, credentials=ExternalCredentials(),
        ssl=True, ssl_options=ssl_options))
    return scmb_connection


def test_cert():
# Create and bind to queue
    EXCHANGE_NAME = 'scmb'
    ROUTE = 'scmb.alerts.#'
    try:
        scmb_conn = scmb_connect()
        channel =  scmb_conn.channel()
        queue = channel.queue_declare(auto_delete=True)
        channel.queue_bind(
            queue=queue.method.queue,
            exchange=EXCHANGE_NAME,
            routing_key=ROUTE)
        channel.close()
        scmb_conn.close()
    except Exception:
        logging.exception("Failed to test scmb connenction")
        sys.exit(1)

def consume_message(ch, method, properties, body):
    body =  json.loads(body.decode('utf-8'))
    print(json.dumps(body, indent=4))

def listen_scmb():
    try:
        scmb_conn = scmb_connect()
        ch = scmb_conn.channel()

        queue_name = ch.queue_declare(auto_delete=True)

        EXCHANGE_NAME = 'scmb'
        ROUTE = 'scmb.alerts.#'

        ch.queue_bind(queue=queue_name.method.queue, exchange=EXCHANGE_NAME, routing_key=ROUTE)

        ch.basic_consume(consume_message, queue=queue_name.method.queue)
        ch.start_consuming()
    except KeyboardInterrupt:
        ch.close()
        scmb_conn.close()
    except Exception:
        logging.exception("Failed to listen to scmb messages")


if __name__ == '__main__':
    print('loading config')
    util.load_config('redfish.conf')
    print("config settings")
    print(util.config)
    if check_cert_exist():
        print('SCMB certs already exists testing connection...')
    else:
        print('SCMB certs not found. Generating/getting certs....')
        get_cert()
        print('Got certs. Testing connection...')
    test_cert()
    listen_scmb()