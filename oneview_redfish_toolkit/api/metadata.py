#!./redfish-venv/bin/python
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

# Python libs
import re
from xml.dom import minidom
import xml.etree.ElementTree as ET


# Project libs
from oneview_redfish_toolkit import util


class Metadata(object):
    """Creates a redfish $metadata XML

    """

    def __init__(self, reference_list):
        """Constructor

            Populates self.redfish with a hardcoded odata values
        """

        metadata = ET.Element("edmx:Edmx")
        metadata.set(
            "xmlns:edmx", "http://docs.oasis-open.org/odata/ns/edmx")
        metadata.set("Version", "4.0")
        for key in reference_list:
            Reference = ET.SubElement(metadata, "edmx:Reference")
            Reference.set(
                "Uri", "http://redfish.dmtf.org/schemas/v1/{}.xml".format(key))
            Include = ET.SubElement(Reference, "edmx:Include")
            Include.set("Namespace", key)
            if key.find('Collection') == -1:
                Include2 = ET.SubElement(Reference, "edmx:Include")
                FileVersion = re.search(
                    '.+\.v(\d+_\d+_\d+)\.json', reference_list[key]).group(1)
                FileVersion = FileVersion.replace("_", ".")
                Include2.set("Namespace", key + "." + FileVersion)
        Reference = ET.SubElement(metadata, "edmx:Reference")
        Reference.set(
            "Uri", "http://redfish.dmtf.org/schemas/v1/RedfishExtensions.xml")
        Include = ET.SubElement(Reference, "edmx:Include")
        Include.set("Namespace", "RedfishExtensions.1.0.0")
        Include.set("Alias", "RedfishExtensions")
        DataServices = ET.SubElement(metadata, "edmx:DataServices")
        Schema = ET.SubElement(DataServices, "Schema")
        Schema.set("NameSpace", "Service")
        EntityContainer = ET.SubElement(Schema, "EntityContainer")
        EntityContainer.set("Name", "Service")
        EntityContainer.set("Extends", "ServiceRoot.1.0.0.ServiceContainer")

        self.metadata = metadata

    def serialize(self):
        xml_str = ET.tostring(self.metadata, encoding="UTF-8").decode("UTF-8")
        # If prettify
        if util.config['redfish']['xml_prettify'] == "True":
            return minidom.parseString(xml_str).toprettyxml(
                encoding="UTF-8", indent="    ").decode("UTF-8")
        else:
            return xml_str
