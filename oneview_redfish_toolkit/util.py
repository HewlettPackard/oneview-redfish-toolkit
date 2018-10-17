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
import appdirs
import logging
import logging.config
import OpenSSL
import os
import pkg_resources
import socket

# Modules own libs
from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.event_dispatcher import EventDispatcher


# Globals vars:
#   globals()['subscriptions_by_type']
#   globals()['all_subscriptions']
#   globals()['delivery_retry_attempts']
#   globals()['delivery_retry_interval']

globals()['subscriptions_by_type'] = {
    "ResourceUpdated": {},
    "ResourceAdded": {},
    "ResourceRemoved": {},
    "Alert": {}
}

globals()['all_subscriptions'] = {}

API_VERSION = 600

CFG_DIR_NAME = 'oneview-redfish-toolkit'


def get_subscriptions_by_type():
    return globals()['subscriptions_by_type']


def get_all_subscriptions():
    return globals()['all_subscriptions']


def get_delivery_retry_attempts():
    return globals()['delivery_retry_attempts']


def get_delivery_retry_interval():
    return globals()['delivery_retry_interval']


def load_event_service_info():
    """Loads Event Service information

        Loads DeliveryRetryAttempts and DeliveryRetryIntervalSeconds
        from CONFIG file and store it in a global var.

        Exceptions:
            OneViewRedfishError: DeliveryRetryAttempts and
            DeliveryRetryIntervalSeconds must be integers greater than zero.
    """
    app_config = config.get_config()
    event_service = dict(app_config.items("event_service"))

    try:
        delivery_retry_attempts = \
            int(event_service["DeliveryRetryAttempts"])
        delivery_retry_interval = \
            int(event_service["DeliveryRetryIntervalSeconds"])

        if delivery_retry_attempts <= 0 or delivery_retry_interval <= 0:
            raise OneViewRedfishError(
                "DeliveryRetryAttempts and DeliveryRetryIntervalSeconds must"
                " be an integer greater than zero.")
    except ValueError:
        raise OneViewRedfishError(
            "DeliveryRetryAttempts and DeliveryRetryIntervalSeconds "
            "must be valid integers.")

    globals()['delivery_retry_attempts'] = delivery_retry_attempts
    globals()['delivery_retry_interval'] = delivery_retry_interval


def generate_certificate(dir_name, file_name, key_length, key_type="rsa"):
    """Create self-signed cert and key files

        Args:
            dir_name: name of the directory to store the files
            file_name: name of the files that will be created. It will append
                .crt to certificate file and .key to key file
            key_length: key length in bits
            key_type: crypto type: RSA or DSA; defaults to RSA
        Returns:
            Nothing
        Exceptions:
            Raise exceptions on error
    """

    app_config = config.get_config()
    private_key = OpenSSL.crypto.PKey()
    if key_type == "rsa":
        private_key.generate_key(OpenSSL.crypto.TYPE_RSA, key_length)
    elif key_type == "dsa":
        private_key.generate_key(OpenSSL.crypto.TYPE_DSA, key_length)
    else:
        message = "Invalid key_type"
        logging.error(message)
        raise OneViewRedfishError(message)

    if not app_config.has_option("ssl-cert-defaults", "commonName"):
        app_config["ssl-cert-defaults"]["commonName"] = get_ip()

    cert = OpenSSL.crypto.X509()
    cert_subject = cert.get_subject()

    cert_defaults = dict(app_config.items("ssl-cert-defaults"))

    for key, value in cert_defaults.items():
        setattr(cert_subject, key, value)

    cert.set_serial_number(1)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(private_key)
    cert.sign(private_key, "sha1")

    # Save Files
    with open(os.path.join(dir_name, file_name + ".crt"), "wt") as f:
        f.write(OpenSSL.crypto.dump_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert).decode("UTF-8"))
    with open(os.path.join(dir_name, file_name + ".key"), "wt") as f:
        f.write(OpenSSL.crypto.dump_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, private_key).decode("UTF-8"))


def get_ip():
    """Tries to detect default route IP Address"""
    s = socket.socket(type=socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except Exception as e:
        logging.exception(e)
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def dispatch_event(event):
    """Creates an EventDispatcher for each subscriber of the event

        Args:
            event: The Event schema describing the JSON payload
            which will be send to the event subscribers.

        Returns:
            Nothing
    """
    # Event resource contains only ONE EventRecord
    events = event.redfish['Events']
    event_record = events[0]

    subscriptions = \
        globals()['subscriptions_by_type'][event_record['EventType']].values()

    for subscription in subscriptions:
        dispatcher = EventDispatcher(
            event,
            subscription,
            globals()['delivery_retry_attempts'],
            globals()['delivery_retry_interval'])

        dispatcher.start()


def get_app_path():
    try:
        source = \
            pkg_resources.resource_filename("oneview_redfish_toolkit", "")
        return source
    except Exception:
        return ""


def get_user_directory():
    return appdirs.user_config_dir(CFG_DIR_NAME)
