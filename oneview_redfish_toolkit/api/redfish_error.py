#!./redfish-venv/bin/python
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

import collections

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.errors import \
    OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator
from oneview_redfish_toolkit import config


class RedfishError(RedfishJsonValidator):
    """Creates a Redfish Error Dict

        Populates self.redfish with errors. Will not validate as there's no
        schema to validate against.

    """

    SCHEMA_NAME = None

    def __init__(self, code, message):
        """Constructor

            Populates self.redfish with error message.
        """

        super().__init__(self.SCHEMA_NAME)
        self.redfish["error"] = collections.OrderedDict()
        # Check if Code is a valid Code Error in the registry
        if code not in config.get_registry_dict()["Base"]["Messages"]:
            raise OneViewRedfishResourceNotFoundError(code, "registry")
        self.redfish["error"]["code"] = "Base.1.1." + code
        self.redfish["error"]["message"] = message
        self.redfish["error"]["@Message.ExtendedInfo"] = list()

    def add_extended_info(
        self,
        message_id,
        message_args=[],
        related_properties=[]):
        """Adds an item to ExtendedInfo list using values from DMTF registry

            Adds an item to ExtendedInfo list using the values for Message,
            Severity and Resolution from DMTF Base Registry.

            Parameters:
                message_id: Id of the message; oneOf the keys in Redfish
                    Registry Messages
                message_args: List of string to replace markers on Redfish
                    messages. Must have the same length as the number of %
                    signs found in the registry Message field
                related_properties: Properties relates to this e error if
                    necessary

        """
        messages = config.get_registry_dict()["Base"]["Messages"]

        # Verify if message_id exists in registry
        try:
            severity = messages[message_id]["Severity"]
        except Exception:
            raise OneViewRedfishResourceNotFoundError(
                message_id,
                "message_id")

        message = messages[message_id]["Message"]

        # Check if numbers of replacemets and message_args length match
        replaces = message.count('%')
        replacements = len(message_args)
        if replaces != replacements:
            raise OneViewRedfishError(
                'Message has {} replacements to be made but {} args '
                'where sent'.
                format(replaces, replacements))
        # Replacing the marks in the message. A better way to do this
        # is welcome.
        for i in range(replaces):
            message = message.replace('%' + str(i + 1), message_args[i])

        # Construct the dict
        extended_info = collections.OrderedDict()
        extended_info["@odata.type"] = "#Message.v1_0_5.Message"
        extended_info["MessageId"] = "Base.1.1." + message_id
        extended_info["Message"] = message
        extended_info["RelatedProperties"] = related_properties
        extended_info["MessageArgs"] = message_args
        extended_info["Severity"] = severity
        extended_info["Resolution"] = messages[message_id]["Resolution"]

        # Append it to the list
        self.redfish["error"]["@Message.ExtendedInfo"].append(extended_info)
