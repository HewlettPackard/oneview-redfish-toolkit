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
from oneview_redfish_toolkit.api.redfish_json_validator \
    import RedfishJsonValidator


class Thermal(RedfishJsonValidator):
    """Creates a Thermal Redfish dict

        Populates self.redfish with Thermal data retrieved from OneView
    """

    SCHEMA_NAME = 'Thermal'

    def __init__(self, utilization, uuid, name):
        """Thermal constructor

            Populates self.redfish with the contents of utilization or
            topology dict.

            Args:
                utilization: Hardware utilization or topology dict from OneView
        """
        super().__init__(self.SCHEMA_NAME)

        self.redfish["@odata.type"] = self.get_odata_type()
        self.redfish["Id"] = uuid
        self.redfish["Name"] = name + " Thermal"
        self.redfish["Temperatures"] = list()
        self.redfish["Temperatures"].append(collections.OrderedDict())
        self.redfish["Temperatures"][0]["@odata.id"] = \
            "/redfish/v1/Chassis/" + uuid + "/Thermal/Temperatures/0"
        self.redfish["Temperatures"][0]["MemberId"] = "0"
        self.redfish["Temperatures"][0]["Name"] = "AmbientTemperature"
        self.redfish["Temperatures"][0]["Status"] = collections.OrderedDict()
        self.redfish["Temperatures"][0]["Status"]["State"] = "Enabled"
        self.redfish["Temperatures"][0]["Status"]["Health"] = "OK"
        self.redfish["Temperatures"][0]["PhysicalContext"] = "Intake"
        if name is not 'Rack':
            self.redfish["Temperatures"][0]["ReadingCelsius"] = \
                utilization["metricList"][0]["metricSamples"][0][1]
            self.redfish["Temperatures"][0]["UpperThresholdCritical"] = \
                utilization["metricList"][0]["metricCapacity"]
            self.redfish["Temperatures"][0]["MinReadingRangeTemp"] = 10
            self.redfish["Temperatures"][0]["MaxReadingRangeTemp"] = 35
        else:
            self.redfish["Temperatures"][0]["ReadingCelsius"] = \
                utilization["peakTemp"]
        self.redfish["@odata.context"] = \
            "/redfish/v1/$metadata#Thermal.Thermal"
        self.redfish["@odata.id"] = "/redfish/v1/Chassis/" + uuid + "/Thermal"

        self._validate()
