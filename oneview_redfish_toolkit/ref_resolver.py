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

from argparse import ArgumentParser
import glob
import json
import re


def ref_resolver(path_to_json):
    """Changes the Redfish JSON Schemas to use locally references"""

    if path_to_json[-1] == '/':
        path_to_json += '*.json'
    else:
        path_to_json += '/*.json'

    paths = glob.glob(path_to_json)

    if not paths:
        print('No JSON found!')
    else:
        for path in paths:
            file_name = path.split('/')[-1]
            json_name = file_name.split('.')[0]

            with open(path, 'r+') as json_file:
                result = json.dumps(
                    json.load(json_file), default=lambda o: o.__dict__,
                    sort_keys=False, indent=4)
                result = re.sub(
                    r'"#/definitions/{}"'.format(json_name),
                    '"{}#/definitions/{}"'.format(
                        file_name, json_name), result)
                result = re.sub(
                    r'\bhttp://redfish.dmtf.org/schemas/v1/\b', '', result)

                json_file.seek(0)
                json_file.write(result)
                json_file.truncate()

        print('Redfish JSON changed with success!')


def main():
    """Gets the path of Redfish JSON Schemas and call ref_resolver function"""

    parser = ArgumentParser()

    parser.add_argument("-p", "--path", dest="path_to_json",
                        help="Path to Redfish JSON Schemas", required=True)
    args = parser.parse_args()

    ref_resolver(args.path_to_json)


if __name__ == '__main__':
    main()
