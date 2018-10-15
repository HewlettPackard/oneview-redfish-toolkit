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

import copy
import json

from flask_api import status

from oneview_redfish_toolkit.blueprints import zone_collection
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestZoneCollection(BaseFlaskTest):
    """Tests for ZoneCollection blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestZoneCollection, self).setUpClass()

        self.app.register_blueprint(zone_collection.zone_collection)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplates.json'
        ) as f:
            self.server_profile_template_list = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ZoneCollection.json'
        ) as f:
            self.zone_collection_mockup = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/LogicalEnclosures.json'
        ) as f:
            self.logical_encl_list = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview'
                '/DriveEnclosureList.json'
        ) as f:
            self.drive_enclosure_list = json.load(f)

    def test_get_zone_collection_when_get_templates_raises_error(self):
        """Tests ZoneCollection when server profile templates raises error"""

        self.oneview_client.server_profile_templates.get_all.side_effect = \
            Exception("An exception has occurred")

        with open(
            'oneview_redfish_toolkit/mockups/errors/Error500.json'
        ) as f:
            error_500 = json.load(f)

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(error_500, result)

    def test_get_zone_collection(self):
        """Tests ZoneCollection"""

        ov_api = self.oneview_client

        ov_api.logical_enclosures.get_all.return_value = \
            self.logical_encl_list

        ov_api.server_profile_templates.get_all.return_value = \
            self.server_profile_template_list
        ov_api.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        self.assertEqualMockup(self.zone_collection_mockup, result)

        ov_api.drive_enclosures.get_all.assert_called_with()
        ov_api.logical_enclosures.get_all.assert_called_with()

    def test_get_zone_collection_empty(self):
        """Tests ZoneCollection with an empty list"""

        self.oneview_client.server_profile_templates.get_all.return_value = \
            []

        with open(
            'oneview_redfish_toolkit/mockups/redfish/ZoneCollectionEmpty.json'
        ) as f:
            zone_collection_empty_mockup = json.load(f)

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(zone_collection_empty_mockup, result)

    def test_get_zone_collection_without_drive_enclosure_associated(self):
        ov_api = self.oneview_client
        ov_api.logical_enclosures.get_all.return_value = \
            self.logical_encl_list

        zone_collection_mockup = copy.deepcopy(self.zone_collection_mockup)
        zone_collection_mockup["Members@odata.count"] = 1
        del zone_collection_mockup["Members"][:2]

        ov_api.server_profile_templates.get_all.return_value = \
            self.server_profile_template_list
        ov_api.drive_enclosures.get_all.return_value = []

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(zone_collection_mockup, result)

        ov_api.drive_enclosures.get_all.assert_called_with()
        ov_api.logical_enclosures.get_all.assert_called_with()

    def test_get_zone_collection_with_drive_enclosure_without_drives(self):
        ov_api = self.oneview_client

        ov_api.logical_enclosures.get_all.return_value = \
            self.logical_encl_list

        zone_collection_mockup = copy.deepcopy(self.zone_collection_mockup)
        zone_collection_mockup["Members@odata.count"] = 1
        del zone_collection_mockup["Members"][:2]
        drive_enclosure_list = copy.deepcopy(self.drive_enclosure_list)
        del drive_enclosure_list[:1]
        drive_enclosure_list[0]["driveBays"] = 0

        ov_api.server_profile_templates.get_all.return_value = \
            self.server_profile_template_list
        ov_api.drive_enclosures.get_all.return_value = \
            drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)

        self.assertEqualMockup(zone_collection_mockup, result)

        ov_api.drive_enclosures.get_all.assert_called_with()
        ov_api.logical_enclosures.get_all.assert_called_with()

    def test_get_zone_collection_mixed_mode(self):
        ov_api = self.oneview_client

        spt_list = \
            copy.deepcopy(self.server_profile_template_list)
        spt_list[1]["localStorage"]["controllers"][0]["mode"] = "Mixed"

        ov_api.logical_enclosures.get_all.return_value = \
            self.logical_encl_list

        ov_api.server_profile_templates.get_all.return_value = \
            spt_list
        ov_api.drive_enclosures.get_all.return_value = \
            self.drive_enclosure_list

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/")

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(self.zone_collection_mockup, result)

        ov_api.drive_enclosures.get_all.assert_called_with()
        ov_api.logical_enclosures.get_all.assert_called_with()
