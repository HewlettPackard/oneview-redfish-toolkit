#!./redfish-venv/bin/python
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

import collections

from oneview_redfish_toolkit.api.redfish_json_validator import \
    RedfishJsonValidator


class Odata(RedfishJsonValidator):
    """Creates a hardcoded odata redfish dict

        Populates self.redfish with a hardcoded odata values. These should
        have all service offered by the servers.

    """

    SCHEMA_NAME = None

    def __init__(self):
        """Constructor

            Populates self.redfish with a hardcoded odata values
        """

        super().__init__(self.SCHEMA_NAME)
        self.redfish["@odata.context"] = "/redfish/v1/$metadata"
        self.redfish["value"] = list()
        self._append_item_to_value_list(
            name="Service",
            kind="Singleton",
            url="/redfish/v1/"
        )
        self._append_item_to_value_list(
            name="Systems",
            kind="Singleton",
            url="/redfish/v1/Systems"
        )
        self._append_item_to_value_list(
            name="Chassis",
            kind="Singleton",
            url="/redfish/v1/Chassis"
        )
        self._append_item_to_value_list(
            name="Managers",
            kind="Singleton",
            url="/redfish/v1/Managers"
        )

    def _append_item_to_value_list(self, name, kind, url):
        od = collections.OrderedDict()
        od["name"] = name
        od["kind"] = kind
        od["url"] = url
        self.redfish["value"].append(od)
