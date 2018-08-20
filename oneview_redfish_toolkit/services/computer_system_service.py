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
import time

from hpOneView.resources.servers.server_profiles import ServerProfiles


DELAY_TO_WAIT_IN_SEC = 3


class ComputerSystemService(object):
    """Represents a Service class of ComputerSystem"""

    def __init__(self, oneview_client):
        """ComputerSystemService constructor

            Args:
                oneview_client: client of Oneview SDK
        """
        self.ov_client = oneview_client

    @staticmethod
    def get_storage_controller(server_profile_tmpl):
        """Returns the local storage controller of Server Profile Template

            If not controller is present, the value returned is None

            Args:
                server_profile_tmpl: the Server Profile Template
        """
        for controller in server_profile_tmpl["localStorage"]["controllers"]:
            if controller["deviceSlot"] != "Embedded":
                return controller

        return None

    def create_composed_system(self, server_profile):
        """Creates a Composed System to Redfish (Creating a Server Profile to OV)

            Args:
                server_profile: the Server Profile to be created

            Returns:
                (task, resource_uri): Tuple with task dict from Oneview and
                    resource_uri of server profile created.
                    The resource_uri can be None if the task has errors before
                    the server profile be created.
        """
        task, _ = self.ov_client.connection.post(
            ServerProfiles.URI,
            server_profile)
        resource_uri = task["associatedResource"]["resourceUri"]

        while not task.get("taskErrors") and not resource_uri:
            time.sleep(DELAY_TO_WAIT_IN_SEC)
            task = self.ov_client.tasks.get(task["uri"])
            resource_uri = task["associatedResource"]["resourceUri"]

        return task, resource_uri
