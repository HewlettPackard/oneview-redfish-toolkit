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
import configparser

from oneview_redfish_toolkit.app import app

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read('redfish.conf')
    except Exception:
        print("Failed to load config file. Aborting...")
        exit(1)

    try:
        port = int(config["redfish"]["redfish_port"])
    except Exception:
        print("Port must be an integer number between 1 and 65536")
        exit(1)
    # Checking port range
    if port < 1 or port > 65536:
        print("Port must be an integer number between 1 and 65536")
        exit(1)

    ssl_type = config["ssl"]["SSLType"]
    # Check SSLType:
    if ssl_type not in ('disabled', 'adhoc', 'certs'):
        print("Invalid SSL type: {}. Must be one of: None, adhoc or certs".
              format(ssl_type))
        exit(1)

    if ssl_type == 'disabled':
        app.run(host="0.0.0.0", port=5000, debug=True)
    elif ssl_type == 'adhoc':
        app.run(host="0.0.0.0", port=5000, debug=True, ssl_context="adhoc")
    else:
        # We should use certs file provided by the user
        ssl_cert_file = config["ssl"]["SSLCertFile"]
        ssl_key_file = config["ssl"]["SSLKeyFile"]
        if ssl_cert_file == "" or ssl_key_file == "":
            print("SSL type: is 'cert' but one of the files are missing on"
                  "the config file. SSLCertFile: {}, SSLKeyFile: {}.".
                  format(ssl_cert_file, ssl_key_file))

        ssl_context = (ssl_cert_file, ssl_key_file)
        app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)
