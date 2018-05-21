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

import logging
import time

from http.client import HTTPConnection
from threading import Thread
from urllib.parse import urlparse


class EventDispatcher(Thread):
    """Dispatches an event to its subscribers"""

    RESPONSE_HEADER = {'Content-Type': 'application/json'}

    def __init__(self, event, subscription, retry_attempts, retry_interval):
        """EventDispatcher constructor

            Dispatches an event to its subscribers.

            Args:
                event: The event object to be dispatched
                subscription: Subscriber information
                retry_attempts: Number of attempts to dispatch the event
                retry_interval: Number in seconds of the interval between
                each retry attempt
        """
        Thread.__init__(self)

        self.event = event
        self.subscription = subscription
        self.retry_attempts = retry_attempts
        self.retry_interval = retry_interval

    def run(self):
        attempts_counter = 0
        done = False

        try:
            url = urlparse(self.subscription.redfish['Destination'])
            json_str = self.event.serialize()

            while (attempts_counter < self.retry_attempts and not done):
                attempts_counter += 1

                try:
                    connection = HTTPConnection(url.hostname, port=url.port)
                    connection.request(
                        'POST', url.path, json_str, self.RESPONSE_HEADER)

                    done = True
                except Exception as e:
                    logging.exception(
                        'Could not dispatch event to {}. '
                        'Error: {}'.format(url.netloc, e))

                    time.sleep(self.retry_interval)
                finally:
                    connection.close()
        except Exception as e:
            logging.exception(
                'Error getting event and/or subscriber information: {}'
                .format(e))
