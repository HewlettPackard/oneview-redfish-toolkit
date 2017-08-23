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


import collections
import json
import jsonschema


class RedfishJsonValidator(object):
    '''Validates a json object against a Redfish schema

        Base class for redfish classes. Have a builtin validate method and a
        serialize method.
        Creates and emmty OrderedDict called redfish which must be populated
        with the redfish data for validation.
        The Serrialize method always validates the redfish content before
        generating the json string, It returns the redfish json string on
        successful validation and raises an exception on validatrion failure
    '''

    def __init__(self, schema_obj):
        '''Constructor

            Adds the schema_obj to itself and creates and empty OrderedDict
            named redfish to be populates with the redfish data to create
            the redfish json

            Args:
                schema_obj: An object containg the redfish schema to be used
                            to validate the redfish json created
        '''

        self.schema_obj = schema_obj
        self.redfish = collections.OrderedDict()

    def _Validate(self):
        '''Validates self.redfish against self.schema_obj

            Validates a redfish OrderedDict agains the schema object passed
            on the object creation

            Returns:
                True on sucess

            Exception:
                reises an exception on validation failure
        '''

        try:
            jsonschema.validate(self.redfish, self.schema_obj)
            return True
        except Exception as e:
            raise(e.message)

    def Serialize(self, pretty=False):
        '''Generates a json string from redfish content

            Validates the content of redfish and generates a json string from
            it on successful validation

            Args:
                pretty: bool value that defines if the generated json string
                        should be indented for better visualizations

            Returns:
                string: json string with the contents of self.redfish
        '''

        self._Validate()
        if pretty:
            indent = 4
        else:
            indent = None
        json_str = json.dumps(self.redfish, default=lambda o: o.__dict__,
                              sort_keys=False, indent=indent)
        return (json_str)
