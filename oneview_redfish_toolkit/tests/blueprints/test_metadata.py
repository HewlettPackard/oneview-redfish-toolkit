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
import collections
from unittest import mock

# 3rd party libs
from flask_api import status

# Module libs
from oneview_redfish_toolkit.blueprints.metadata import metadata
from oneview_redfish_toolkit.tests.base_flask_test import BaseFlaskTest


schemas_dict = collections.OrderedDict()
schemas_dict["ComputerSystemCollection"] = \
    "ComputerSystemCollection.json"
schemas_dict["ComputerSystem"] = "ComputerSystem.v1_4_0.json"


class Metadata(BaseFlaskTest):
    """Tests for Metadata blueprint"""

    @classmethod
    def setUpClass(self):
        super(Metadata, self).setUpClass()

        self.app.register_blueprint(metadata)

    @mock.patch('oneview_redfish_toolkit.api.schemas.SCHEMAS', schemas_dict)
    def test_get_metadata(self):
        """Tests Metadata blueprint result against know value """

        response = self.client.get("/redfish/v1/$metadata")

        result = response.data.decode("utf-8")

        with open(
            'oneview_redfish_toolkit/mockups/redfish/Metadata.xml'
        ) as f:
            metadata_mockup = f.read()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("text/xml", response.mimetype)
        self.assertEqual(metadata_mockup, result)
