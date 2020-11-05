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
from unittest.mock import call

from flask_api import status
from hpOneView import HPOneViewException

from hpOneView.resources.servers.enclosures import Enclosures
from hpOneView.resources.servers.server_profile_templates import ServerProfileTemplate

from oneview_redfish_toolkit.blueprints import zone
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


class TestZone(BaseFlaskTest):
    """Tests for Zone blueprint"""

    @classmethod
    def setUpClass(self):
        super(TestZone, self).setUpClass()

        self.app.register_blueprint(zone.zone)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'ServerProfileTemplate.json'
        ) as f:
            self.server_profile_template = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/Enclosure.json'
        ) as f:
            self.enclosure = json.load(f)

        with open(
            'oneview_redfish_toolkit/mockups/oneview/'
            'DriveEnclosureByIndexAssociationWithEnclosure.json'
        ) as f:
            self.drive_encl_assoc = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'ServerHardwareList.json'
        ) as f:
            sh_list = json.load(f)
            self.server_hardware_list = sh_list[:4]

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'DrivesByDriveEnclosure.json'
        ) as f:
            self.drives = json.load(f)

        with open(
                'oneview_redfish_toolkit/mockups/oneview/'
                'Volumes.json'
        ) as f:
            self.volumes = json.load(f)

        self.spt_id = self.server_profile_template["uri"].split("/")[-1]

    def test_get_zone_when_uuid_is_template_id_with_enclosure_id(self):
        """Tests get a Zone when the zone uuid is template id + enclosure id"""

        api_client = self.oneview_client

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Zone.json'
        ) as f:
            zone_mockup = json.load(f)

        enclosure_obj = Enclosures(self.oneview_client, self.enclosure)
        api_client.enclosures.get_by_id.return_value = enclosure_obj

        spt_obj = ServerProfileTemplate(
            self.oneview_client, self.server_profile_template)
        api_client.server_profile_templates.get_by_id.return_value = \
            spt_obj

        api_client.server_hardware.get_all.return_value = \
            self.server_hardware_list
        api_client.connection.get.side_effect = [
            self.drive_encl_assoc,
            self.drives
        ]
        api_client.volumes.get_all.return_value = []

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/" +
            self.spt_id + "-" + self.enclosure["uuid"])

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(zone_mockup, result)

        api_client.enclosures.get_by_id.assert_called_with(
            self.enclosure["uuid"])
        api_client.server_profile_templates.get_by_id.assert_called_with(
            self.spt_id)
        api_client.connection.get.assert_has_calls(
            [
                call("/rest/index/associations/resources?parenturi=" +
                     self.enclosure["uri"] + "&category=drive-enclosures"),
                call('/rest/index/resources?category=drives&count=10000'
                     '&filter="driveEnclosureUri:'
                     '/rest/drive-enclosures/SN123100"')
            ]
        )
        api_client.server_hardware.get_all.assert_called_with(
            filter=[
                "locationUri='/rest/enclosures/0000000000A66101'",

                "serverHardwareTypeUri='"
                + self.server_profile_template["serverHardwareTypeUri"] + "'"
            ])

    def test_get_zone_when_uuid_is_only_template_id(self):
        """Tests get a Zone when the zone uuid is only template id"""

        api_client = self.oneview_client

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'ZoneWithoutDrives.json'
        ) as f:
            zone_without_drives_mockup = json.load(f)

        spt_obj = ServerProfileTemplate(
            self.oneview_client, self.server_profile_template)
        api_client.server_profile_templates.get_by_id.return_value = \
            spt_obj

        api_client.server_hardware.get_all.return_value = \
            self.server_hardware_list
        api_client.connection.get.side_effect = [
            self.drive_encl_assoc,
            self.drives
        ]
        api_client.volumes.get_all.return_value = []

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/" + self.spt_id)

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(zone_without_drives_mockup, result)

        api_client.enclosures.get_by_id.assert_not_called()
        api_client.server_profile_templates.get_by_id.assert_called_with(
            self.spt_id)
        api_client.connection.get.assert_not_called()
        api_client.server_hardware.get_all.assert_called_with(
            filter=[
                "serverGroupUri='"
                + self.server_profile_template["enclosureGroupUri"] + "'",

                "serverHardwareTypeUri='"
                + self.server_profile_template["serverHardwareTypeUri"] + "'"
            ])

    def test_get_zone_when_drive_enclosures_assoc_is_empty(self):
        """Tests get a Zone when drive enclosures by enclosure is empty"""

        api_client = self.oneview_client

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'ZoneWithoutDrivesAssignedYet.json'
        ) as f:
            zone_without_drives_mockup = json.load(f)

        enclosure_obj = Enclosures(self.oneview_client, self.enclosure)
        api_client.enclosures.get_by_id.return_value = enclosure_obj

        spt_obj = ServerProfileTemplate(
            self.oneview_client, self.server_profile_template)
        api_client.server_profile_templates.get_by_id.return_value = \
            spt_obj

        drive_encl_by_encl = copy.copy(self.drive_encl_assoc)
        drive_encl_by_encl["members"] = []
        api_client.connection.get.side_effect = [
            drive_encl_by_encl,
            self.drives
        ]
        api_client.server_hardware.get_all.return_value = \
            self.server_hardware_list

        api_client.volumes.get_all.return_value = []

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/" +
            self.spt_id + "-" + self.enclosure["uuid"])

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(zone_without_drives_mockup, result)

        api_client.enclosures.get_by_id.assert_called_with(
            self.enclosure["uuid"])
        api_client.server_profile_templates.get_by_id.assert_called_with(
            self.spt_id)
        api_client.connection.get.assert_has_calls([
            call("/rest/index/associations/resources?parenturi="
                 + self.enclosure["uri"]
                 + "&category=drive-enclosures")
        ])
        api_client.server_hardware.get_all.assert_called_with(
            filter=[
                "locationUri='/rest/enclosures/0000000000A66101'",

                "serverHardwareTypeUri='"
                + self.server_profile_template["serverHardwareTypeUri"] + "'"
            ])

    def test_get_zone_not_found(self):
        """Tests Zone when UUID was not found"""

        self.oneview_client.server_profile_templates.get_by_id.side_effect = \
            HPOneViewException({
                'errorCode': 'RESOURCE_NOT_FOUND',
                'message': 'SPT not found'
            })

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/" +
            self.spt_id)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_zone_when_enclosure_not_found(self):
        """Tests Zone when UUID was not found due the enclosure not found"""

        self.oneview_client.server_profile_templates.get_by_id.side_effect = \
            HPOneViewException({
                'errorCode': 'RESOURCE_NOT_FOUND',
                'message': 'Enclosure not found'
            })

        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/" +
            self.spt_id + "/" + self.enclosure["uuid"])

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual("application/json", response.mimetype)

    def test_get_zone_when_external_storage_attached(self):
        """Tests get a Zone when the zone uuid is only template id"""

        api_client = self.oneview_client

        with open(
                'oneview_redfish_toolkit/mockups/redfish/'
                'ZoneWithExternalStorage.json'
        ) as f:
            zone_with_external_storage_mockup = json.load(f)

        enclosure_obj = Enclosures(self.oneview_client, self.enclosure)
        api_client.enclosures.get_by_id.return_value = enclosure_obj

        spt_obj = ServerProfileTemplate(
            self.oneview_client, self.server_profile_template)
        api_client.server_profile_templates.get_by_id.return_value = \
            spt_obj

        api_client.server_hardware.get_all.return_value = \
            self.server_hardware_list
        api_client.connection.get.side_effect = [
            self.drive_encl_assoc,
            self.drives
        ]
        api_client.volumes.get_all.return_value = \
            self.volumes
        response = self.client.get(
            "/redfish/v1/CompositionService/ResourceZones/" + self.spt_id
            + "-" + self.enclosure["uuid"])

        result = json.loads(response.data.decode("utf-8"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqualMockup(zone_with_external_storage_mockup, result)
