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


# 3rd party libs
from flask import Blueprint

# own libs
from oneview_redfish_toolkit.api.composition_service \
    import CompositionService
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder


composition_service = Blueprint("composition_service", __name__)


@composition_service.route("/redfish/v1/CompositionService/", methods=["GET"])
def get_composition_service():
    """Get the Redfish Composition Service.

        Get method to return Composition Service JSON when
        /redfish/v1/CompositionService is requested.

        Returns:
            JSON: Redfish JSON with CompositionService.
    """
    # Build Composition Service object and validates it
    cs = CompositionService()

    ResponseBuilder.success(cs)