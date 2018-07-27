#!./redfish-venv/bin/python
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

# Python libs
import re
from xml.dom import minidom
import xml.etree.ElementTree as ET

# Project libs
from oneview_redfish_toolkit import config


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
            reference = ET.SubElement(metadata, "edmx:Reference")
            reference.set(
                "Uri",
                "http://redfish.dmtf.org/schemas/v1/{}_v1.xml".format(key))
            include = ET.SubElement(reference, "edmx:Include")
            include.set("Namespace", key)
            if key.find('Collection') == -1:
                include2 = ET.SubElement(reference, "edmx:Include")
                file_version = re.search(
                    '.+\.v(\d+_\d+_\d+)\.json', reference_list[key]).group(1)
                file_version = file_version.replace("_", ".")
                include2.set("Namespace", key + "." + file_version)
        reference = ET.SubElement(metadata, "edmx:Reference")
        reference.set(
            "Uri",
            "http://redfish.dmtf.org/schemas/v1/RedfishExtensions_v1.xml")
        include = ET.SubElement(reference, "edmx:Include")
        include.set("Namespace", "RedfishExtensions.1.0.0")
        include.set("Alias", "RedfishExtensions")
        data_services = ET.SubElement(metadata, "edmx:DataServices")
        schema = ET.SubElement(data_services, "Schema")
        schema.set("NameSpace", "Service")
        entity_container = ET.SubElement(schema, "EntityContainer")
        entity_container.set("Name", "Service")
        entity_container.set("Extends", "ServiceRoot.1.0.0.ServiceContainer")

        self.metadata = metadata

    def serialize(self):
        xml_str = ET.tostring(self.metadata, encoding="UTF-8").decode("UTF-8")
        # If prettify
        if config.get_config()['redfish']['xml_prettify'] == "True":
            return minidom.parseString(xml_str).toprettyxml(
                encoding="UTF-8", indent="    ").decode("UTF-8")
        else:
            return xml_str
