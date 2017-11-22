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
import glob
import os

import collections
import json
import jsonschema

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit import util


class RedfishJsonValidator(object):
    """Validates a json object against a Redfish schema

        Base class for redfish classes. Have a builtin validate method and a
        serialize method.
        Creates and empty OrderedDict called redfish which must be populated
        with the redfish data for validation.
        The Serialize method always validates the redfish content before
        generating the json string, It returns the redfish json string on
        successful validation and raises an exception on validation failure
    """

    def __init__(self, schema_name):
        """Constructor

            Adds the schema_obj to itself and creates and empty OrderedDict
            named redfish to be populates with the redfish data to create
            the redfish json

            Args:
                schema_name: The redfish schema name to be used
                            to validate the redfish json created
        """

        if schema_name is None:
            self.schema_obj = None
        else:
            self.schema_obj = util.schemas_dict[schema_name]
        self.redfish = collections.OrderedDict()

    def _validate(self):
        """Validates self.redfish against self.schema_obj

            Validates a redfish OrderedDict against the schema object passed
            on the object creation.

            Returns:
                None

            Exception:
                raises an exception on validation failure
        """
        schema_dir = util.config['redfish']['schema_dir']
        schema_paths = glob.glob(os.getcwd() + '/' + schema_dir + '/*.json')

        store = {}

        for path in schema_paths:
            with open(path) as schema_file:
                json_schema = json.load(schema_file)

            file_name = path.split('/')[-1]
            store["http://redfish.dmtf.org/schemas/v1/" + file_name] = \
                json_schema

        resolver = jsonschema.RefResolver(
            'file://%s/' % (os.getcwd() + '/' + schema_dir),
            self.schema_obj, store=store)

        if self.schema_obj is None:
            raise OneViewRedfishError(
                "Can't serialize without a schema object. Schema name was"
                " set to None at object instantiation.")

        jsonschema.validate(self.redfish, self.schema_obj, resolver=resolver)

    def serialize(self):
        """Generates a json string from redfish content

            Serialize the contents of self.redfish. Uses the value of
            indent_json from redfish section of ini file to indent or
            not the result.

            Returns:
                string: json string with the contents of self.redfish
        """

        if util.config['redfish']['indent_json']:
            indent = 4
        else:
            indent = None
        return json.dumps(
            self.redfish,
            default=lambda o: o.__dict__,
            sort_keys=False,
            indent=indent
        )
