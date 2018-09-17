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

STATUS_MAP = {
    "OK": {
        "State": "Enabled",
        "Health": "OK"
    },
    "Disabled": {
        "State": "Disabled",
        "Health": "Warning"
    },
    "Warning": {
        "State": "Enabled",
        "Health": "Warning"
    },
    "Critical": {
        "State": "Enabled",
        "Health": "Critical"
    },
    "Unknown": {
        "State": "Absent",
        "Health": None
    }
}

HEALTH_STATE = {
    "Critical": "Critical",
    "OK": "OK",
    "Unknown": "Warning",
    "Disabled": "Warning",
    "Warning": "Warning",
}

MANAGER_HEALTH_STATE = {
    "INFO": "OK",
    "WARNING": "Warning",
    "CRITICAL": "Critical",
}

COMPOSITION_STATE = {
    "NoProfileApplied": "Unused",
    "ApplyingProfile": "Composing",
    "ProfileApplied": "Composed",
    "ProfileError": "Failed",
    "RemovingProfile": "Composed"
}


SERVER_HARDWARE_STATE_TO_REDFISH_STATE = {
    "NoProfileApplied": "Enabled",
    "Monitored": "Enabled",
    "ProfileApplied": "Enabled",
    "Unsupported": "UnavailableOffline",
    "Unknown": "Absent",
    "RemoveFailed": "StandbyOffline",
    "ProfileError": "StandbyOffline",
    "Unmanaged": "StandbyOffline",
    "Removing": "Updating",
    "ApplyingProfile": "Updating",
    "RemovingProfile": "Updating",
    "UpdatingFirmware": "Updating",
    "Adding": "Updating",
    "Removed": "Disabled"
}

SERVER_PROFILE_STATE_TO_REDFISH_STATE = {
    "Normal": "Enabled",
    "Creating": "Updating",
    "Updating": "Updating",
    "Deleting": "Updating",
    "CreateFailed": "StandbyOffline",
    "UpdateFailed": "StandbyOffline",
    "DeleteFailed": "StandbyOffline"
}

APPLIANCE_STATE_TO_REDFISH_STATE = {
    "OK": "Enabled",
    "UPGRADE": "Updating",
    "RESTORE": "Updating",
    "FACTORY_RESET": "Updating",
    "FAILOVER": "Updating",
    "CONFIGURATION_ERROR": "StandbyOffline",
    "RESTORE_NO_RESET_ERROR": "StandbyOffline",
    "NETWORK_ERROR": "StandbyOffline",
    "INCOMPATIBLE_MODEL_ERROR": "UnavailableOffline",
    "STOPPED": "UnavailableOffline",
    "ERROR": "UnavailableOffline",
    "STARTING": "Starting",
}

CRITICALITY_STATUS = {
    "OK": 1,
    "Warning": 2,
    "Critical": 3
}


def get_redfish_server_hardware_status_struct(resource):
    sh_state = SERVER_HARDWARE_STATE_TO_REDFISH_STATE.get(
        resource["state"])
    health_status = HEALTH_STATE.get(resource["status"])

    return sh_state, health_status


def get_redfish_server_profile_state(resource):
    sp_state = SERVER_PROFILE_STATE_TO_REDFISH_STATE.get(
        resource["state"])
    health_status = HEALTH_STATE.get(resource["status"])
    return sp_state, health_status


def get_redfish_composition_state(resource):
    composition_state = COMPOSITION_STATE.get(
        resource["state"])
    return composition_state
