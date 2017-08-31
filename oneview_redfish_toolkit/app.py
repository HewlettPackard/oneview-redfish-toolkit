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
import os

from flask import Flask

import logging

from oneview_redfish_toolkit.api.redfish_base_api import redfish_base
from oneview_redfish_toolkit.blueprints.service_root import service_root
from oneview_redfish_toolkit import util

util.configure_logging(os.getenv("LOGGING_FILE",
                                 "oneview_redfish_toolkit/logging.ini"))

cfg = util.load_config('oneview_redfish_toolkit/redfish.ini')

if cfg is None:
    logging.error("Could not load config file. Exiting")
    exit(1)

schemas = dict(cfg.items('schemas'))
schemas_dict = util.load_schemas(cfg['directories']['schema_dir'], schemas)

if schemas_dict is None:
    logging.error("Could not schemas. Exiting")
    exit(1)

app = Flask(__name__)

app.schemas_dict = schemas_dict

app.register_blueprint(redfish_base)
app.register_blueprint(service_root, url_prefix='/redfish/v1/')
