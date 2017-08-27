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

from flask import Flask

from oneview_redfish_toolkit.blueprints.computer_system_collection \
    import computer_system_collection
from oneview_redfish_toolkit.blueprints.redfish_base import redfish_base
from oneview_redfish_toolkit.blueprints.service_root import service_root

from oneview_redfish_toolkit import util

"""
JSON Schemas
"""
cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')

if cfg is None:
    print("Could not load config file. Exiting")
    exit(1)

schemas = dict(cfg.items('schemas'))
schemas_dict = util.load_schemas(cfg['directories']['schema_dir'], schemas)

if schemas_dict is None:
    print("Could not load schemas. Exiting")
    exit(1)

"""
OneView config
"""
oneview_config = dict(cfg.items('oneview_config'))
credentials = dict(cfg.items('credentials'))
oneview_config["credentials"] = credentials

"""
Flask application
"""
app = Flask(__name__)

app.schemas_dict = schemas_dict
app.oneview_config = oneview_config

"""
Register blueprints
"""
app.register_blueprint(redfish_base, url_prefix="/redfish")
app.register_blueprint(service_root, url_prefix='/redfish/v1/')
app.register_blueprint(computer_system_collection,
                       url_prefix='/redfish/v1/Systems')
