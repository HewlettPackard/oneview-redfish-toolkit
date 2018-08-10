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
import collections
import json
import jsonschema

from oneview_redfish_toolkit.api.errors import OneViewRedfishError
from oneview_redfish_toolkit.api.errors \
    import OneViewRedfishResourceNotFoundError
from oneview_redfish_toolkit.api import schemas
from oneview_redfish_toolkit import config


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

        self.schema_name = schema_name
        self.redfish = collections.OrderedDict()

    def _validate(self):
        """Validates self.redfish against self.schema_obj

            Validates a redfish OrderedDict against the schema object passed
            on the object creation.

            Returns:
                None

            Exception:
                ValidationError: Raises this exception on validation failure.

                OneViewRedfishError: Raises this exception if
                schema is not found.
        """
        self.validate(self.redfish, self.schema_name)

    @staticmethod
    def validate(dict_to_validate, schema_name):
        """Validates a dict against a schema corresponding to the schema_name

            Returns:
                None

            Exception:
                ValidationError: Raises this exception on validation failure.

                OneViewRedfishError: Raises this exception if
                schema is not found.
        """
        stored_schemas = config.get_stored_schemas()
        schema_obj = RedfishJsonValidator.get_schema_obj(schema_name)

        resolver = jsonschema.RefResolver('', schema_obj, store=stored_schemas)
        jsonschema.validate(dict_to_validate, schema_obj, resolver=resolver)

    def serialize(self):
        """Generates a json string from redfish content

            Serialize the contents of self.redfish. Uses the value of
            indent_json from redfish section of ini file to indent or
            not the result.

            Returns:
                string: json string with the contents of self.redfish
        """

        if config.get_config()['redfish']['indent_json']:
            indent = 4
        else:
            indent = None
        return json.dumps(
            self.redfish,
            default=lambda o: o.__dict__,
            sort_keys=False,
            indent=indent)

    def get_resource_by_id(self, resource_list,
                           resource_number_key, resource_id):
        """Gets a specific resource in the resource list

            Validates the resource ID and gets the resource in
            the resource list.

            Args:
                resource_list: List of resources.
                resource_number_key: Field name of the resource
                    number in the JSON.
                resource_id: Resource's ID that will be searched
                    in the resource list.

            Returns:
                Resource in the list.

            Exception:
                OneViewRedfishError: If the ID is not an integer.
                OneViewRedfishResourceNotFoundError: If the resource
                    was not found.
        """
        try:
            resource_id = int(resource_id)
        except ValueError:
            raise OneViewRedfishError("Invalid {} ID".format(
                self.__class__.__name__))

        for resource in resource_list:
            if resource[resource_number_key] == resource_id:
                return resource

        raise OneViewRedfishResourceNotFoundError(
            "Object", self.__class__.__name__)

    def get_odata_type(self):
        """Retrieves odata.type from schema file

            Retrieves the odata.type defined on the schema file
            for the class attribute schema name.

            Returns:
                string: odata.type for the class schema name.
        """
        return self.get_odata_type_by_schema(self.schema_name)

    def get_odata_type_by_schema(self, schema_name):
        """Retrieves odata.type from schema file

            Retrieves the odata.type defined on the schema file
            for the schema name received as parameter.

            Returns:
                string: odata.type for the schema name .
        """
        schema_obj = self.get_schema_obj(schema_name)
        return schema_obj['title']

    @staticmethod
    def get_schema_obj(schema_name):
        """Retrieves schemas object for the schema name

            Retrieves the schema file content loaded
            as a dict for the schema name receveid
            as parameter.

            Returns:
                dict: schema dict for the schema name.
        """
        schema_file = schemas.SCHEMAS[schema_name]
        stored_schemas = config.get_stored_schemas()

        try:
            schema_obj = stored_schemas[
                "http://redfish.dmtf.org/schemas/v1/" + schema_file]
        except KeyError:
            raise OneViewRedfishError("{} not found".format(schema_file))

        return schema_obj
