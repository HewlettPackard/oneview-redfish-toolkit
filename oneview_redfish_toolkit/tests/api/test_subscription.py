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

"""
    Tests for test_subscription.py
"""

import json

from oneview_redfish_toolkit.api.subscription \
    import Subscription
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestSubscription(BaseTest):
    """Tests for Subscription class"""

    def setUp(self):
        """Tests preparation"""

        # Loading Subscription result mockup
        with open(
            'oneview_redfish_toolkit/mockups/redfish/'
            'Subscription.json'
        ) as f:
            self.subscription_mockup = json.load(f)

    def test_class_instantiation(self):
        # Tests if class is correctly instantiated and validated

        try:
            subscription = Subscription("", "", [], None)
        except Exception as e:
            self.fail("Failed to instantiate Subscription class."
                      " Error: {}".format(e))
        self.assertIsInstance(subscription, Subscription)

    def test_serialize(self):
        # Tests the serialize function result against known result

        try:
            subscription = Subscription(
                "e7f93fa2-0cb4-11e8-9060-e839359bc36a",
                "http://www.dnsname.com/Destination1",
                ["Alert", "ResourceUpdated"], None)
        except Exception as e:
            self.fail("Failed to instantiate Subscription class."
                      " Error: {}".format(e))

        try:
            result = json.loads(subscription.serialize())
        except Exception as e:
            self.fail("Failed to serialize. Error: ".format(e))

        self.assertEqualMockup(self.subscription_mockup, result)
