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

from unittest import mock
from unittest import TestCase

from oneview_redfish_toolkit import config


class BaseTest(TestCase):
    """Base test"""

    @classmethod
    def setUpClass(cls):
        patcher = mock.patch('oneview_redfish_toolkit.connection.'
                             'check_oneview_availability')
        cls.mock_check_availability = patcher.start()

        cls.config_file = './oneview_redfish_toolkit/conf/redfish.conf'

        config.load_config(cls.config_file)

    def assertEqualMockup(self, first, second, msg=None):
        if type(first) is dict and type(second) is dict:
            first['@odata.type'] = ''
            second['@odata.type'] = ''

        super(BaseTest, self).assertEqual(first, second, msg)
