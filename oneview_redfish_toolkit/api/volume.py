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
from flask import abort
from flask import g

from flask_api import status
from hpOneView.resources.resource import ResourceClient
from oneview_redfish_toolkit.api.computer_system import ComputerSystem


from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator
from oneview_redfish_toolkit.api.resource_block_collection import \
    ResourceBlockCollection

import oneview_redfish_toolkit.api.status_mapping as status_mapping


class Volume(RedfishJsonValidator):
    """Creates a Volume Redfish dict

        Populates self.redfish with Volume data
    """

    SCHEMA_NAME = 'Volume'
    METADATA_INFO = "/redfish/v1/$metadata#Volume.Volume"

    def __init__(self, data):
        """Volume constructor

            Populates self.redfish and validates the result

            Args:
                data: a dict with Redfish's Volume data
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish.update(data)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["@odata.context"] = self.__class__.METADATA_INFO

        self._validate()

    @staticmethod
    def build_volume_for_resource_blocks(resource_block_id, volume):
        """Returns a storage Volume with the contents of data from an Oneview

            Args:
                resource_block_id: storage volume uuid
                volume: storage volume

        """
        attrs = {}
        attrs["@odata.id"] = ResourceBlockCollection.BASE_URI + "/" + \
            resource_block_id + "/Storage/1/Volumes/1"
        attrs["Id"] = "1"
        attrs["Identifiers"] = list()
        attrs["Identifiers"].append({
            "DurableNameFormat": "UUID",
            "DurableName": volume["uri"].split("/")[-1]
        })
        attrs["CapacityBytes"] = int(volume["provisionedCapacity"])
        attrs["Name"] = volume["name"]
        attrs["Status"] = collections.OrderedDict()
        map_struct = status_mapping.STATUS_MAP.get(volume["status"])
        attrs["Status"]["State"] = map_struct["State"]
        attrs["Status"]["Health"] = map_struct["Health"]

        raidlevel = get_raid_level_for_storage_volume(volume)
        if raidlevel:
            attrs["VolumeType"] = status_mapping.RAID_LEVEL.get(raidlevel)
        else:
            attrs["VolumeType"] = "RawDevice"

        return Volume(attrs)

    @staticmethod
    def build_volume_details(uuid, volume_id):
        """Returns a Volume with the contents of data from an Oneview

            Args:
                uuid: Server Profile uuid
                volume_id: Volume id

        """

        server_profile = g.oneview_client.server_profiles.get_by_id(uuid).data
        sas_logical_jbod = get_sas_logical_jbod_by_volumeid(server_profile,
                                                            volume_id)

        if sas_logical_jbod is None:
            abort(status.HTTP_404_NOT_FOUND, "Volume {} not found"
                  .format(volume_id))

        sas_Logical_Interconnect_Uri = \
            sas_logical_jbod["sasLogicalInterconnectUri"]

        drivepaths = []
        for logical_Drive_Bay_Uri in sas_logical_jbod["logicalDriveBayUris"]:
            drivepath = get_drive_path_from_logical_Drive_Bay_Uri(
                logical_Drive_Bay_Uri)
            drivepaths.append(drivepath)

        drive_enclosure_uri = \
            get_drive_enclosure_uri_from_sas_Logical_Interconnect(
                sas_Logical_Interconnect_Uri)

        drive_enclosure_object = get_drive_enclosure_object(
            drive_enclosure_uri)

        drivebayuris = get_drivebayuris_from_drive_enclosure_object(
            drivepaths, drive_enclosure_object)
        device_slot = get_device_slot_from_sas_logical_jbod_by_volumeid(
            server_profile, volume_id)
        raidlevel = get_raidLevel(server_profile, device_slot, volume_id)
        attrs = {}
        attrs["@odata.id"] = ComputerSystem.BASE_URI + "/" + uuid + \
            "/Storage/1/Volumes/" + volume_id
        attrs["Id"] = volume_id
        attrs["Name"] = sas_logical_jbod["name"]
        attrs["Status"] = collections.OrderedDict()
        map_struct = status_mapping.STATUS_MAP.get(sas_logical_jbod["status"])
        attrs["Status"]["State"] = map_struct["State"]
        attrs["Status"]["Health"] = map_struct["Health"]
        if raidlevel is not None:
            attrs["VolumeType"] = status_mapping.RAID_LEVEL.get(raidlevel)
        else:
            attrs["VolumeType"] = "RawDevice"
        attrs["CapacityBytes"] = get_capacity_in_bytes(
            sas_logical_jbod["maxSizeGB"])
        attrs["Identifiers"] = list()
        attrs["Identifiers"].append(
            {"DurableNameFormat": "UUID",
             "DurableName": sas_logical_jbod["uri"].split("/")[-1]})
        attrs["Links"] = collections.OrderedDict()
        attrs["Links"]["Drives"] = list()

        for drivebayuri in drivebayuris:
            attrs["Links"]["Drives"].append(
                {
                    "@odata.id": ComputerSystem.BASE_URI + "/" + uuid +
                    "/Storage/1/Drives/" + drivebayuri.split("/")[-1]
                }
            )

        return Volume(attrs)

    @staticmethod
    def build_external_storage_volume_details(sp_uuid, volume, volume_id):
        """Returns a storage Volume with the contents of data from an Oneview

            Args:
                sp_uuid: server profile uuid
                volume: storage volume
                volume_id: storage_volume_id

        """
        attrs = {}
        attrs["@odata.id"] = ComputerSystem.BASE_URI + "/" + \
            sp_uuid + "/Storage/1/Volumes/" + volume_id
        attrs["Id"] = volume_id
        attrs["Identifiers"] = list()
        attrs["Identifiers"].append({
            "DurableNameFormat": "UUID",
            "DurableName": volume_id
        })
        attrs["CapacityBytes"] = int(volume["provisionedCapacity"])
        attrs["Name"] = volume["name"]
        attrs["Status"] = collections.OrderedDict()
        map_struct = status_mapping.STATUS_MAP.get(volume["status"])
        attrs["Status"]["State"] = map_struct["State"]
        attrs["Status"]["Health"] = map_struct["Health"]

        raidlevel = get_raid_level_for_storage_volume(volume)
        if raidlevel:
            attrs["VolumeType"] = status_mapping.RAID_LEVEL.get(raidlevel)
        else:
            attrs["VolumeType"] = "RawDevice"

        return Volume(attrs)


def get_sas_logical_jbod_by_volumeid(server_profile, volume_id):

    for logical_jbod in server_profile["localStorage"]["sasLogicalJBODs"]:
        if logical_jbod["id"] == int(volume_id) and \
                logical_jbod["sasLogicalJBODUri"]:
            item = g.oneview_client.sas_logical_jbods\
                .get(logical_jbod["sasLogicalJBODUri"])
            return item

    return None


def get_device_slot_from_sas_logical_jbod_by_volumeid(server_profile,
                                                      volume_id):

    for logical_jbod in server_profile["localStorage"]["sasLogicalJBODs"]:
        if logical_jbod["id"] == int(volume_id):
            return logical_jbod["deviceSlot"]

    return None


def get_drive_path_from_logical_Drive_Bay_Uri(logical_Drive_Bay_Uri):
    ov_client = g.oneview_client
    conn = ov_client.connection
    URI = logical_Drive_Bay_Uri
    resource_client = ResourceClient(conn, URI)
    item = resource_client.get(URI)
    return item["drivePaths"][0]


def get_drive_enclosure_uri_from_sas_Logical_Interconnect(
        sas_Logical_Interconnect_Uri):
    item = g.oneview_client.sas_logical_interconnects.get_by_uri(
        sas_Logical_Interconnect_Uri).data
    return item["driveEnclosureUris"][0]


def get_drive_enclosure_object(drive_enclosure_uri):
    item = g.oneview_client.drive_enclosures.get(drive_enclosure_uri)
    return item


def get_capacity_in_bytes(capacity_in_gb):
    size_in_bytes = float(capacity_in_gb) * 1024 * 1024 * 1024
    return int(size_in_bytes)


def get_drivebayuris_from_drive_enclosure_object(drivepaths,
                                                 drive_enclosure_object):
    drivebayuris = []
    for drivebay in drive_enclosure_object["driveBays"]:
        # eliminating drive = NONE condition to avoid TypeError: 'NoneType' object is not subscriptable
        if isinstance(drivebay["drive"], dict):
            for drivepath in drivebay["drive"]["drivePaths"]:
                if drivepath in drivepaths:
                    drivebayuri = drivebay["uri"]
                    drivebayuris.append(drivebayuri)
    return drivebayuris


def get_raidLevel(server_profile, device_slot, volume_id):
    for storagecontroller in server_profile["localStorage"]["controllers"]:
        if(storagecontroller["deviceSlot"] == device_slot):
            for logicaldrive in storagecontroller["logicalDrives"]:
                if logicaldrive["sasLogicalJBODId"] == int(volume_id):
                    raidlevel = logicaldrive["raidLevel"]
                    return raidlevel
    return None


def get_raid_level_for_storage_volume(volume):
    raidLevel = None
    storage_pool = g.oneview_client.storage_pools.get_by_uri(
        volume["storagePoolUri"]).data
    if storage_pool:
        deviceSpecifications = storage_pool["deviceSpecificAttributes"]
        if deviceSpecifications.get("supportedRAIDLevel"):
            raidLevel = deviceSpecifications["supportedRAIDLevel"]
    return raidLevel
