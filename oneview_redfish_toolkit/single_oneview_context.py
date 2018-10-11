# -*- coding: utf-8 -*-

# Copyright (2018) Hewlett Packard Enterprise Development LP
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
import logging

# 3rd party libs
from flask import g

# Modules own libs
from oneview_redfish_toolkit.config import PERFORMANCE_LOGGER_NAME


def single_oneview(original_func):
    """Python decorator for endpoints with single OneView context"""
    def new_function(*args, **kwargs):
        """Function to set single OneView context"""
        logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
            "in Single OneView Context")
        set_single_oneview_context()
        return original_func(*args, **kwargs)

    new_function.__name__ = original_func.__name__
    return new_function


def set_single_oneview_context():
    """Set to use the same OneView IP in the same request"""
    g.single_oneview_context = True


def is_single_oneview_context():
    """Check if it ot be used the same OneView IP on the request context"""
    return 'single_oneview_context' in g


def get_single_oneview_ip():
    """Get the same OneView's IP in request context"""
    if 'single_oneview_ip' in g:
        return g.single_oneview_ip
    return None


def set_single_oneview_ip(oneview_ip):
    """Set OneView's IP to be used in the same request context"""
    if not get_single_oneview_ip():
        g.single_oneview_ip = oneview_ip
