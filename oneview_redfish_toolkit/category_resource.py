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
import threading


lock = threading.Lock()

map_category_resources_ov = None


class CategoryResource(object):
    def __init__(self, resource_id, resource, function):
        self.resource_id = resource_id
        self.resource = resource
        self.function = function


def init_map_category_resources():
    global map_category_resources_ov
    map_category_resources_ov = dict()


def _get_map_category_resources():
    return map_category_resources_ov


def set_map_category_resources_entry(resource_id, resource, function):
    # Check if the resource's category is already cached
    if get_category_by_resource_id(resource_id):
        return

    with lock:
        global map_category_resources_ov
        map_category_resources_ov[resource_id] = \
            CategoryResource(resource_id, resource, function)


def get_category_by_resource_id(resource_id):
    """Get cached resource category by resource ID"""
    cached_category = _get_map_category_resources().get(resource_id)

    return cached_category
