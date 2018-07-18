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
from copy import deepcopy

from flask_api import status
from werkzeug.exceptions import abort

from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.api.util.power_option import \
    RESET_ALLOWABLE_VALUES_LIST


class ComputerSystem(RedfishJsonValidator):
    """Creates a Computer System Redfish dict

        Populates self.redfish with ComputerSystem data retrieved from oneview
    """

    SCHEMA_NAME = 'ComputerSystem'
    BASE_URI = '/redfish/v1/Systems'

    def __init__(self, server_hardware, server_hardware_types, server_profile, drives):
        """ComputerSystem constructor

            Populates self.redfish with the contents of ServerHardware and
            ServerHardwareTypes dicts.

            Args:
                server_hardware: ServerHardware dict from OneView
                server_hardware_types: ServerHardwareTypes dict from OneView
                server_profile: ServerProfile dict from OneView.
                drives: Drives list from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        base_resource = server_profile
        self.server_hardware = server_hardware
        self.resource_block_uuids = list()
        self.resource_block_uuids.append(self.server_hardware["uuid"])
        self._fill_spt_on_resource_blocks_uuids_list(base_resource["description"])
        self._fill_drives_on_resource_blocks_uuids_list(drives)
        self.redfish["@odata.type"] = "#ComputerSystem.v1_4_0.ComputerSystem"
        self.redfish["Id"] = base_resource["uuid"]
        self.redfish["Name"] = base_resource["name"]
        self.redfish["SystemType"] = "Composed"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = server_hardware["model"]
        self.redfish["SerialNumber"] = server_hardware["serialNumber"]
        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = \
            status_mapping.get_redfish_state(base_resource["status"])
        self.redfish["Status"]["Health"] = \
            status_mapping.get_redfish_health(server_hardware["status"])
        self.redfish["PowerState"] = server_hardware["powerState"]
        self.redfish["Boot"] = collections.OrderedDict()
        self.redfish["Boot"]["BootSourceOverrideTarget@Redfish."
                             "AllowableValues"] = \
            self.map_boot(server_hardware_types['bootCapabilities'])
        self.redfish["BiosVersion"] = server_hardware["romVersion"]
        self.redfish["ProcessorSummary"] = collections.OrderedDict()
        self.redfish["ProcessorSummary"]['Count'] = \
            server_hardware["processorCount"]
        self.redfish["ProcessorSummary"]["Model"] = \
            server_hardware["processorType"]
        self.redfish["MemorySummary"] = collections.OrderedDict()
        self.redfish["MemorySummary"]["TotalSystemMemoryGiB"] = \
            server_hardware["memoryMb"] / 1024
        self.redfish["Storage"] = collections.OrderedDict()
        self.redfish["Storage"]["@odata.id"] = \
            self.BASE_URI + "/" + base_resource['uuid'] + "/Storage"
        self.redfish["EthernetInterfaces"] = collections.OrderedDict()
        self.redfish["EthernetInterfaces"]["@odata.id"] = \
            self.BASE_URI + "/" + \
            base_resource['uuid'] + \
            "/EthernetInterfaces"
        self.redfish["NetworkInterfaces"] = collections.OrderedDict()
        self.redfish["NetworkInterfaces"]["@odata.id"] = \
            self.BASE_URI + "/" + \
            base_resource['uuid'] + \
            "/NetworkInterfaces"
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["Links"]["Chassis"] = list()
        self.redfish["Links"]["Chassis"].append(collections.OrderedDict())
        self.redfish["Links"]["Chassis"][0]["@odata.id"] = \
            "/redfish/v1/Chassis/" + server_hardware['uuid']
        self.redfish["Links"]["ManagedBy"] = list()
        self.redfish["Links"]["ManagedBy"].append(collections.OrderedDict())
        self.redfish["Links"]["ManagedBy"][0]["@odata.id"] = \
            "/redfish/v1/Managers/" + server_hardware['uuid']
        self.redfish["Links"]["ResourceBlocks"] = list()
        self._fill_resource_block_members(self.resource_block_uuids)
        self.redfish["Actions"] = collections.OrderedDict()
        self.redfish["Actions"]["#ComputerSystem.Reset"] = \
            collections.OrderedDict()
        self.redfish["Actions"]["#ComputerSystem.Reset"]["target"] = \
            self.BASE_URI + "/" + \
            base_resource["uuid"] + \
            "/Actions/ComputerSystem.Reset"
        self.redfish["Actions"]["#ComputerSystem.Reset"][
            "ResetType@Redfish.AllowableValues"] = \
            RESET_ALLOWABLE_VALUES_LIST
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#ComputerSystem.ComputerSystem"
        self.redfish["@odata.id"] = self.BASE_URI + "/" \
            + base_resource["uuid"]

        self._validate()

    def map_boot(self, boot_list):
        """Maps Oneview's boot options to Redfish's boot option

            Maps the known OneView boot options to Redfish boot option.
            If a unknown boot option shows up it will be mapped to None

            Args:
                boot_list: List with OneView boot options

            Returns:
                list with Redfish boot options
        """

        redfish_oneview_boot_map = dict()
        redfish_oneview_boot_map['PXE'] = 'Pxe'
        redfish_oneview_boot_map['CD'] = 'Cd'
        redfish_oneview_boot_map['HardDisk'] = 'Hdd'
        redfish_oneview_boot_map['FibreChannelHba'] = 'RemoteDrive'
        redfish_oneview_boot_map['Floppy'] = 'Floppy'
        redfish_oneview_boot_map['USB'] = 'Usb'
        redfish_boot_list = list()

        try:
            for boot_option in boot_list:
                redfish_boot_list.append(
                    redfish_oneview_boot_map[boot_option])
        except Exception:
            redfish_boot_list.append('None')

        return redfish_boot_list

    @staticmethod
    def build_server_profile(profile_name,
                             server_profile_template,
                             system_blocks,
                             network_blocks,
                             storage_blocks):
        server_profile = deepcopy(server_profile_template)

        server_profile.pop("uri", None)
        server_profile.pop("serverProfileDescription", None)
        server_profile.pop("created", None)
        server_profile.pop("modified", None)
        server_profile.pop("status", None)
        server_profile.pop("state", None)
        server_profile.pop("scopesUri", None)
        server_profile.pop("eTag", None)
        if isinstance(server_profile.get("connectionSettings"), dict):
            server_profile["connectionSettings"].pop('manageConnections', None)

        server_profile["name"] = profile_name
        server_profile["description"] = server_profile_template["uri"]
        server_profile["type"] = "ServerProfileV8"
        server_profile["category"] = "server-profiles"
        server_profile["serverHardwareUri"] = \
            "/rest/server-hardware/" + system_blocks[0]["uuid"]
        server_profile["localStorage"]["sasLogicalJBODs"] = \
            ComputerSystem._build_sas_logical_jbods(server_profile_template,
                                                    storage_blocks)

        return server_profile

    @staticmethod
    def _build_sas_logical_jbods(server_profile_template, storage_blocks):
        sas_logical_jbods = []

        controller = ComputerSystem._get_storage_controller(
            server_profile_template)

        if not controller:
            abort(status.HTTP_412_PRECONDITION_FAILED,
                  "The server profile template should be controllers "
                  "configured properly")

        for index, storage_block in enumerate(storage_blocks):
            storage_id = index + 1
            attributes = storage_block["attributes"]

            storage = {
                "id": storage_id,
                "name": "Storage " + str(storage_id),
                "deviceSlot": controller["deviceSlot"],
                "numPhysicalDrives": 1,
                "driveMinSizeGB": attributes["capacityInGB"],
                "driveMaxSizeGB": attributes["capacityInGB"],
                "driveTechnology": attributes["interfaceType"].capitalize()
                                   + attributes["mediaType"].capitalize()
            }

            sas_logical_jbods.append(storage)

        return sas_logical_jbods

    @staticmethod
    def _get_storage_controller(server_profile_tmpl):
        for controller in server_profile_tmpl["localStorage"]["controllers"]:
            if controller["deviceSlot"] != "Embedded":
                return controller

        return None

    def _fill_resource_block_members(self, resource_block_uuids):
        resource_blocks_base_uri = "/redfish/v1/CompositionService/ResourceBlocks/{}"
        for resource_block_uuid in resource_block_uuids:
            self.redfish["Links"]["ResourceBlocks"].append({
                "@odata.id": resource_blocks_base_uri.format(resource_block_uuid)
            })

    def _fill_spt_on_resource_blocks_uuids_list(self, spt_uuid):
        if spt_uuid:
            self.resource_block_uuids.append(spt_uuid)

    def _fill_drives_on_resource_blocks_uuids_list(self, drives):
        for drive in drives:
            drive_uuid = drive["uri"].split("/")[-1]
            self.resource_block_uuids.append(drive_uuid)
