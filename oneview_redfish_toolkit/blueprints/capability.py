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

from flask import Blueprint
from flask import g

from oneview_redfish_toolkit.api.capability import Capability
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder


capability = Blueprint("capability", __name__)


@capability.route(Capability.BASE_URI + "/<uuid>", methods=["GET"])
def get_capability(uuid):
    """Get the Redfish Capability.

        Return Capability redfish JSON.

        Returns:
            JSON: Redfish json with Capability.
    """
    profile_template = g.oneview_client.server_profile_templates.get(uuid)

    capability = Capability(profile_template)

    return ResponseBuilder.success(capability)
