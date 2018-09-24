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

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection
import oneview_redfish_toolkit.api.status_mapping as status_mapping
from oneview_redfish_toolkit.api.util.power_option import \
    RESET_ALLOWABLE_VALUES_LIST
from oneview_redfish_toolkit.services.computer_system_service import \
    ComputerSystemService


class ComputerSystem(RedfishJsonValidator):
    """Creates a Computer System Redfish dict

        Populates self.redfish with ComputerSystem data retrieved from oneview
    """

    SCHEMA_NAME = 'ComputerSystem'
    BASE_URI = '/redfish/v1/Systems'

    def __init__(self, server_hardware, server_hardware_types,
                 server_profile, drives, server_profile_template_uuid,
                 manager_uuid):
        """ComputerSystem constructor

            Populates self.redfish with the contents of ServerHardware and
            ServerHardwareTypes dicts.

            Args:
                server_hardware: ServerHardware dict from OneView
                server_hardware_types: ServerHardwareTypes dict from OneView
                server_profile: ServerProfile dict from OneView.
                drives: Drives list from OneView
                server_profile_template_uuid: ServerProfileTemplate uuid
                manager_uuid: Oneview's current manager uuid
        """
        super().__init__(self.SCHEMA_NAME)

        base_resource = server_profile
        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = base_resource["uuid"]
        self.redfish["Description"] = base_resource["description"]
        self.redfish["Name"] = base_resource["name"]
        self.redfish["SystemType"] = "Composed"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = server_hardware["model"]
        self.redfish["SerialNumber"] = server_hardware["serialNumber"]
        self.redfish["Status"] = collections.OrderedDict()
        health = self._get_highest_status_for_sp_and_sh(
            status_mapping.HEALTH_STATE.get(base_resource["status"]),
            status_mapping.HEALTH_STATE.get(server_hardware["status"])
        )
        state, _ = status_mapping.\
            get_redfish_server_profile_state(base_resource)
        self.redfish["Status"]["State"] = state
        self.redfish["Status"]["Health"] = health
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
        if manager_uuid:
            self.redfish["Links"]["ManagedBy"].append(
                collections.OrderedDict())
            self.redfish["Links"]["ManagedBy"][0]["@odata.id"] = \
                "/redfish/v1/Managers/" + manager_uuid
        self.redfish["Links"]["ResourceBlocks"] = list()
        self._fill_resource_block_members(drives,
                                          server_hardware,
                                          server_profile_template_uuid)
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

    @staticmethod
    def _get_highest_status_for_sp_and_sh(sp_status, sh_status):
        all_status = dict()
        all_status[sp_status] = \
            status_mapping.CRITICALITY_STATUS[sp_status]
        all_status[sh_status] = \
            status_mapping.CRITICALITY_STATUS[sh_status]

        highest_status = max(all_status, key=(lambda key: all_status[key]))

        return highest_status

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
                             profile_description,
                             server_profile_template,
                             system_block,
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
        server_profile.pop("description", None)
        if isinstance(server_profile.get("connectionSettings"), dict):
            server_profile["connectionSettings"].pop('manageConnections', None)

        server_profile["name"] = profile_name
        if profile_description:
            server_profile["description"] = profile_description
        server_profile["type"] = "ServerProfileV8"
        server_profile["category"] = "server-profiles"
        server_profile["serverHardwareUri"] = \
            "/rest/server-hardware/" + system_block["uuid"]
        server_profile["localStorage"]["sasLogicalJBODs"] = \
            ComputerSystem._build_sas_logical_jbods(server_profile_template,
                                                    storage_blocks)

        return server_profile

    @staticmethod
    def _build_sas_logical_jbods(server_profile_template, storage_blocks):
        sas_logical_jbods = []

        controller = ComputerSystemService.get_storage_controller(
            server_profile_template)

        if storage_blocks and not controller:
            raise OneViewRedfishError(
                "The Server Profile Template should have a valid "
                "storage controller to use the Storage Resource Blocks passed")

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

    def _fill_resource_block_members(self,
                                     drives,
                                     server_hardware,
                                     server_profile_template_uuid):
        resource_block_uuids = \
            self._get_resource_block_uuids(drives,
                                           server_hardware,
                                           server_profile_template_uuid)

        base_uri = ResourceBlockCollection.BASE_URI + "/{}"
        blocks = self.redfish["Links"]["ResourceBlocks"]
        for resource_block_uuid in resource_block_uuids:
            blocks.append({"@odata.id": base_uri.format(resource_block_uuid)})

    def _get_resource_block_uuids(self,
                                  drives,
                                  server_hardware,
                                  server_profile_template_uuid):
        resource_block_uuids = list()
        resource_block_uuids.append(server_hardware["uuid"])

        # fill with network resource block
        if server_profile_template_uuid:
            resource_block_uuids.append(server_profile_template_uuid)

        for drive in drives:
            storage_resource_uuid = drive["uri"].split("/")[-1]
            resource_block_uuids.append(storage_resource_uuid)

        return resource_block_uuids
