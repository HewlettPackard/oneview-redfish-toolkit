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

from flask import Blueprint
from flask import g

from oneview_redfish_toolkit.api.network_adapter_collection \
    import NetworkAdapterCollection
from oneview_redfish_toolkit.blueprints.util.response_builder import \
    ResponseBuilder

network_adapter_collection = Blueprint(
    "network_adapter_collection", __name__)


@network_adapter_collection.route(
    "/redfish/v1/Chassis/<uuid>/NetworkAdapters/", methods=["GET"])
def get_network_adapter_collection(uuid):
    """Get the Redfish Network Adapters Collection.

    Return NetworkAdapterCollection Redfish JSON.
    """

    server_hardware = g.oneview_client.server_hardware.get(uuid)

    nic = NetworkAdapterCollection(server_hardware)

    return ResponseBuilder.success(nic)
