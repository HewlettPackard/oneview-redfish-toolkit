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


class ComputerSystemService(object):
    """Represents a Service class of ComputerSystem"""

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
