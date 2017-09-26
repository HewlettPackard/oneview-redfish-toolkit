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

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
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
                sh_dict: Serverhardware dict from OneView
                sht_dict: ServerHardwareTypes dict from OneViwe
        """
        super().__init__(self.SCHEMA_NAME)

        self.server_hardware = sh_dict

        self.redfish["@odata.type"] = "#ComputerSystem.v1_4_0.ComputerSystem"
        self.redfish["Id"] = sh_dict["uuid"]
        self.redfish["Name"] = sh_dict["name"]
        self.redfish["SystemType"] = "Physical"
        self.redfish["Manufacturer"] = "HPE"
        self.redfish["Model"] = sh_dict["model"]
        self.redfish["SerialNumber"] = sh_dict["serialNumber"]
        # Status must be an object
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
                    redfish_oneview_boot_map[boot_option]
                )
        except Exception:
            redfish_boot_list.append('None')

        return redfish_boot_list

    def get_oneview_power_configuration(self, reset_type):
        reset_type_dict = dict()

        reset_type_dict["On"] = dict()
        reset_type_dict["On"]["powerState"] = "On"
        reset_type_dict["On"]["powerControl"] = "MomentaryPress"

        reset_type_dict["ForceOff"] = dict()
        reset_type_dict["ForceOff"]["powerState"] = "Off"
        reset_type_dict["ForceOff"]["powerControl"] = "PressAndHold"

        reset_type_dict["GracefulShutdown"] = dict()
        reset_type_dict["GracefulShutdown"]["powerState"] = "Off"
        reset_type_dict["GracefulShutdown"]["powerControl"] = "MomentaryPress"

        reset_type_dict["GracefulRestart"] = dict()
        reset_type_dict["GracefulRestart"]["powerState"] = "On"
        reset_type_dict["GracefulRestart"]["powerControl"] = "Reset"

        reset_type_dict["ForceRestart"] = dict()
        reset_type_dict["ForceRestart"]["powerState"] = "On"
        reset_type_dict["ForceRestart"]["powerControl"] = "ColdBoot"

        reset_type_dict["PushPowerButton"] = dict()

        if reset_type == "PushPowerButton":
            if self.server_hardware["powerState"] == "On":
                reset_type_dict["PushPowerButton"]["powerState"] = "Off"
            else:
                reset_type_dict["PushPowerButton"]["powerState"] = "On"

        reset_type_dict["PushPowerButton"]["powerControl"] = "MomentaryPress"

        try:
            return reset_type_dict[reset_type]
        except Exception:
            raise OneViewRedfishError(
                'There is no mapping for {} on the OneView'
                .format(reset_type))
