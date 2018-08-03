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

# Modules own libs
from oneview_redfish_toolkit import multiple_oneview


def first_parameter_resource(resource, function, *args, **kwargs):
    resource_id = args[0]

    return multiple_oneview.query_ov_client_by_resource(resource_id, resource,
                                                        function, *args,
                                                        **kwargs)


def all_oneviews_resource(resource, function, *args, **kwargs):
    all_results = multiple_oneview.search_resource_multiple_ov(resource,
                                                               function, None,
                                                               *args,
                                                               **kwargs)

    return all_results
