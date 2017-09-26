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
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class ComputerSystem(RedfishJsonValidator):
    """Creates a Computer System Redfish dict

        Populates self.redfish with ComputerSystem data retrieved from oneview
    """

    SCHEMA_NAME = 'ComputerSystem'

    def __init__(self, sh_dict, sht_dict):
        """ComputerSystem constructor

            Populates self.redfish with the contents of ServerHardware and
            ServerHardwareTypes dicts.

            Args:
                sh_dict: ServerHardware dict from OneView
                sht_dict: ServerHardwareTypes dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = "#ComputerSystem.v1_4_0.ComputerSystem"
        self.redfish["Id"] = sh_dict["uuid"]
        self.redfish["Name"] = sh_dict["name"]
        self.redfish["SystemType"] = "Physical"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = sh_dict["model"]
        self.redfish["SerialNumber"] = sh_dict["serialNumber"]
        self.redfish["Status"] = collections.OrderedDict()
        self.redfish["Status"]["State"] = "Enabled"
        self.redfish["Status"]["Health"] = sh_dict["status"]
        self.redfish["PowerState"] = sh_dict["powerState"]
        self.redfish["Boot"] = collections.OrderedDict()
        self.redfish["Boot"]["BootSourceOverrideTarget@Redfish."
                             "AllowableValues"] = \
            self.map_boot(sht_dict['bootCapabilities'])
        self.redfish["BiosVersion"] = sh_dict["romVersion"]
        self.redfish["ProcessorSummary"] = collections.OrderedDict()
        self.redfish["ProcessorSummary"]['Count'] = sh_dict["processorCount"]
        self.redfish["ProcessorSummary"]["Model"] = sh_dict["processorType"]
        self.redfish["MemorySummary"] = collections.OrderedDict()
        self.redfish["MemorySummary"]["TotalSystemMemoryGiB"] = \
            sh_dict["memoryMb"] / 1024
        self.redfish["Links"] = collections.OrderedDict()
        self.redfish["Links"]["Chassis"] = list()
        self.redfish["Links"]["Chassis"].append(collections.OrderedDict())
        self.redfish["Links"]["Chassis"][0]["@odata.id"] = \
            "/redfish/v1/Chassis/" + sh_dict['uuid']
        self.redfish["Actions"] = collections.OrderedDict()
        self.redfish["Actions"]["#ComputerSystem.Reset"] = \
            collections.OrderedDict()
        self.redfish["Actions"]["#ComputerSystem.Reset"]["target"] = \
            "/redfish/v1/System/{}/Actions/ComputerSystem.Reset" \
            .format(sh_dict["uuid"])
        self.redfish["Actions"]["#ComputerSystem.Reset"][
            "ResetType@Redfish.AllowableValues"] = \
            ["On", "ForceOff", "GracefulShutdown", "GracefulRestart",
             "ForceRestart", "Nmi", "ForceOn", "PushPowerButton"]

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
