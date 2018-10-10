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

from hpOneView import HPOneViewException
from jsonschema import ValidationError

from hpOneView.resources.servers.server_profiles import ServerProfiles

from oneview_redfish_toolkit.api.errors import NOT_FOUND_ONEVIEW_ERRORS
from oneview_redfish_toolkit.api.util.power_option import OneViewPowerOption
from oneview_redfish_toolkit import config

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
            has_valid_controller_mode = \
                controller["mode"] == "HBA" or controller["mode"] == "Mixed"

            if controller["deviceSlot"] != "Embedded" and \
                    has_valid_controller_mode:
                return controller

        return None

    def power_off_server_hardware(self, sh_uuid_or_uri, on_compose=False):
        """Power off a Oneview Server Hardware based on app configuration

            Args:
                sh_uuid_or_uri: the UUID or URI of Server Hardware to be
                powered off
                on_compose: if True gets configuration for the situation when
                 want to Compose a System; if False gets configuration for the
                 situation when want to Decompose a System

            Returns:
                True|False: if powering off action was applied to Oneview
        """
        if on_compose:
            config_key = 'PowerOffServerOnCompose'
        else:
            config_key = 'PowerOffServerOnDecompose'

        power_off = config.get_composition_settings()[config_key]

        if power_off:
            power_state = \
                OneViewPowerOption.get_power_state_by_reset_type(power_off)

            self.ov_client.server_hardware.update_power_state(power_state,
                                                              sh_uuid_or_uri)

            return True

        return False

    def validate_computer_system_resource_block_to_composition(self,
                                                               system_block):
        """Validates a Computer System Resource Block to be used in a composition

            Args:
                system_block: the Server Hardware that represents a Computer
                System Resource Block
        """
        if system_block["serverProfileUri"]:
            sp_uuid = system_block["serverProfileUri"].split("/")[-1]
            raise ValidationError(
                "Computer System Resource Block already belongs to a "
                "Composed System with ID {}".format(sp_uuid))

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

    def get_server_profile_template_from_sp(self, sp_uri):
        """Gets Sever Profile Template uuid from Server Profile uri"""
        all_sp_labels = self.ov_client.labels.get_by_resource(sp_uri)
        server_profile_template_uuid = ""

        for label in all_sp_labels["labels"]:
            try:
                spt_uuid = label["name"].replace(" ", "-")
                is_valid_spt = \
                    self.ov_client.server_profile_templates.get(spt_uuid)
                if is_valid_spt:
                    server_profile_template_uuid = spt_uuid
                    break
            except HPOneViewException as e:
                if e.oneview_response["errorCode"] in NOT_FOUND_ONEVIEW_ERRORS:
                    pass
                else:
                    raise

        return server_profile_template_uuid
