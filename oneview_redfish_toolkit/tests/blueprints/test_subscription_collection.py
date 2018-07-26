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
from unittest import mock

# 3rd party libs
from flask_api import status

# Module libs
from oneview_redfish_toolkit.blueprints.subscription_collection\
    import subscription_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestSubscriptionCollection(BaseFlaskTest):
    """Tests for SubscriptionCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestSubscriptionCollection, self).setUpClass()

        self.app.register_blueprint(subscription_collection)

    @mock.patch('oneview_redfish_toolkit.util.get_all_subscriptions')
    def test_get_subscription_collection(self, subscriptions_mockup):
        """Tests SubscriptionCollection blueprint result against know value"""

        subscriptions_mockup.return_value = dict()

        response = \
            self.client.get("/redfish/v1/EventService/EventSubscriptions/")

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/SubscriptionCollection.json'
        ) as f:
            subscription_collection_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(subscription_collection_mockup, result)
