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
from oneview_redfish_toolkit.blueprints.subscription import subscription
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestSubscription(BaseFlaskTest):
    """Tests for Subscription blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestSubscription, self).setUpClass()

        self.app.register_blueprint(subscription)

    @mock.patch('uuid.uuid1')
    def test_add_subscription(self, uuid_mockup):
        """Test POST Subscription"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "ResourceUpdated"])),
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/Subscription.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(subscription_mockup, result)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_duplicated_event_types(self, uuid_mockup):
        """Test POST Subscription with duplicated event types"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "Alert", "ResourceUpdated"])),
            content_type='application/json')

        result = json.loads(response.data.decode("utf-8"))

        with open(
                'oneview_redfish_toolkit/mockups/'
                'redfish/Subscription.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(subscription_mockup, result)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_key1(self, uuid_mockup):
        """Test POST Subscription with invalid Destination key"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                INVALID="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "ResourceUpdated"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_key2(self, uuid_mockup):
        """Test POST Subscription with invalid EventTypes key"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                INVALID=["Alert", "ResourceUpdated"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_empty_events(self, uuid_mockup):
        """Test POST Subscription with empty list of EventTypes"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=[])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_events(self, uuid_mockup):
        """Test POST Subscription with invalid EventTypes"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["INVALID"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_with_context(self, uuid_mockup):
        """Test POST Subscription with a Context"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert"],
                Context="WebUser3")),
            content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_add_subscription_invalid_destination(self, uuid_mockup):
        """Test POST Subscription with a invalid Destination URI"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        response = self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="INVALID",
                EventTypes=["Alert"])),
            content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_remove_subscription(self, uuid_mockup):
        """Test REMOVE Subscription"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36b"

        self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "ResourceUpdated"])),
            content_type='application/json')

        delete_response = self.client.delete(
            "/redfish/v1/EventService/EventSubscriptions/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(status.HTTP_200_OK, delete_response.status_code)
        self.assertEqual("application/json", delete_response.mimetype)

        get_response = self.client.get(
            "/redfish/v1/EventService/EventSubscriptions/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36b")

        self.assertEqual(
            status.HTTP_404_NOT_FOUND, get_response.status_code)
        self.assertEqual("application/json", get_response.mimetype)

    def test_remove_subscription_invalid_id(self):
        """Test REMOVE Subscription with invalid ID"""

        response = self.client.delete(
            "/redfish/v1/EventService/EventSubscriptions/INVALID")

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    @mock.patch('uuid.uuid1')
    def test_get_subscription(self, uuid_mockup):
        """Test GET Subscription"""

        uuid_mockup.return_value = "e7f93fa2-0cb4-11e8-9060-e839359bc36a"

        self.client.post(
            "/redfish/v1/EventService/EventSubscriptions/",
            data=json.dumps(dict(
                Destination="http://www.dnsname.com/Destination1",
                EventTypes=["Alert", "ResourceUpdated"])),
            content_type='application/json')

        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/Subscription.json'
        ) as f:
            subscription_mockup = json.loads(f.read())

        response = self.client.get(
            "/redfish/v1/EventService/EventSubscriptions/"
            "e7f93fa2-0cb4-11e8-9060-e839359bc36a")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(subscription_mockup, result)

    def test_get_invalid_subscription(self):
        """Test GET invalid Subscription"""

        response = self.client.get(
            "/redfish/v1/EventService/EventSubscriptions/INVALID")

        self.assertEqual(
            status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)
