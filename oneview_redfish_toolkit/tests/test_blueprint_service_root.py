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

from oneview_redfish_toolkit.app import app
from oneview_redfish_toolkit import util
import unittest


class TestBlueprintServiceRoot(unittest.TestCase):

    def setUp(self):

        cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')

        schemas = dict(cfg.items('schemas'))
        schemas_dict = util.load_schemas(cfg['directories']['schema_dir'],
                                         schemas)

        # creates a test client
        self.app = app.test_client()

        self.app.schemas_dict = schemas_dict
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_service_root(self):
        result = self.app.get("/redfish/v1/")

        json_str = result.data.decode("utf-8")

        with open(
            'oneview_redfish_toolkit/tests/mockups/ServiceRoot.mok'
        ) as F:
            mok_json = F.read()
        self.assertEqual(json_str, mok_json)
