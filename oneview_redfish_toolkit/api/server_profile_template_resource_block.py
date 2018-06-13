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

from oneview_redfish_toolkit.api.resource_block import ResourceBlock


class ServerProfileTemplateResourceBlock(ResourceBlock):
    """Creates a ResourceBlock Redfish dict for Server Profile Template

        Populates self.redfish with some hardcoded ResourceBlock
        values and with Server Profile Template data retrieved from Oneview.
    """

    def __init__(self, server_profile_template):
        """ResourceBlock constructor

            Populates self.redfish with the contents of
            Server Profile Template dict.

            Args:
                server_profile_template: ServerProfileTemplate dict
                from OneView
        """
        super().__init__(server_profile_template)

        self.server_profile_template = server_profile_template

        self.redfish["ResouceBlockType"] = ["Storage", "Network"]

        # TODO(svoboda) check how to fill this attribute
        self.redfish["CompositionStatus"]["CompositionState"] = None

        self.redfish["CompositionStatus"]["SharingCapable"] = True

        self._validate()
