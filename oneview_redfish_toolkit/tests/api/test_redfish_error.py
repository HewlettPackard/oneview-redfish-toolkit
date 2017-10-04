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


import unittest
from unittest import mock


from oneview_redfish_toolkit.api import errors
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit import util


class TestRedfishError(unittest.TestCase):
    """Tests for RedfishError class"""

    @mock.patch.object(util, 'OneViewClient')
    def setUp(self, oneview_client_mockup):
        """Tests preparation"""

        # Loading variable in util module
        util.load_config('redfish.conf')

    def test_class_instantiation(self):
        """Tests class instantiation"""

        try:
            redfish_error = RedfishError("GeneralError", "General Error")
        except Exception as e:
            self.fail("Failed to instantiate RedfishError. Error: ".format(e))
        self.assertIsInstance(redfish_error, RedfishError)

    def test_serialize(self):
        """Tests the serialize function result against known result"""

        redfish_error = RedfishError("GeneralError", "General Error")
        json_str = redfish_error.serialize()

        with open(
            'oneview_redfish_toolkit/mockups_errors/'
            'RedfishErrorNoExtendedInfo.json'
        ) as f:
            redfish_error_mockup = f.read()
        self.assertEqual(redfish_error_mockup, json_str)

    def test_add_extended_info_message_message_args_exclusion_fail(self):
        """Tests the add_extended_info with mutual exclusion of Message failling

            Tests add_extended_info with the mutual exclusion check of Message
            and MessageArgs failling
        """

        redfish_error = RedfishError("GeneralError", "General Error")

        try:
            redfish_error.add_extended_info(
                "GeneralError",
                "General Message",
                ["Conflicting args"])
        except errors.OneViewRedfishError as e:
            self.assertEqual(
                e.msg,
                "Message and MessageArgs are mutual excusive parameters")

    def test_add_extended_info_invalid_error_code(self):
        """Tests the add_extended_info invalid error code"""

        redfish_error = RedfishError("GeneralError", "General Error")

        try:
            redfish_error.add_extended_info(
                "InvalidCode",
                "General Message")
        except errors.OneViewRedfishResourceNotFoundError as e:
            self.assertEqual(
                e.msg,
                "message_id InvalidCode not found")

    def test_add_extended_info_invalid_message_args(self):
        """Tests the add_extended_info invalid message_args"""

        redfish_error = RedfishError("GeneralError", "General Error")

        try:
            redfish_error.add_extended_info(
                message_id="PropertyValueNotInList",
                message_args=["Only 1, need 2"])
        except errors.OneViewRedfishError as e:
            self.assertEqual(
                e.msg,
                'Message has 2 replacements to be made but 1 args where sent')

    def test_add_extended_info_personal_message(self):
        """Tests the add_extended_info invalid message_args"""

        redfish_error = RedfishError("GeneralError", "General Error")

        with open(
            'oneview_redfish_toolkit/mockups_errors/'
            'RedfishErrorPersonalizedMessage.json'
        ) as f:
            redfish_error_mockup = f.read()

        try:
            redfish_error.add_extended_info(
                message_id="PropertyValueNotInList",
                message="Personalized message")
        except errors.OneViewRedfishError as e:
            self.fail("Failled to add Extended info".format(e))

        json_str = redfish_error.serialize()

        self.assertEqual(redfish_error_mockup, json_str)

    def test_redfish_error_with_extended_info(self):
        """Tests the add_extended_info with two aditional info"""

        with open(
            'oneview_redfish_toolkit/mockups_errors/'
            'RedfishErrorExtendedInfo.json'
        ) as f:
            redfish_error_mockup = f.read()

        try:
            redfish_error = RedfishError(
                "GeneralError",
                "A general error has occurred. See ExtendedInfo "
                "for more information.")
            redfish_error.add_extended_info(
                message_id="PropertyValueNotInList",
                message_args=["RED", "IndicatorLED"],
                related_properties=["#/IndicatorLED"])
            redfish_error.add_extended_info(
                message_id="PropertyNotWritable",
                message_args=["SKU"],
                related_properties=["#/SKU"])
        except errors.OneViewRedfishError as e:
            self.fail("Failled to add Extened info".format(e))

        json_str = redfish_error.serialize()

        self.assertEqual(redfish_error_mockup, json_str)
