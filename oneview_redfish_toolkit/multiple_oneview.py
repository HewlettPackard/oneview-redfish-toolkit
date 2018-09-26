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
from collections import OrderedDict
import logging
import threading
import time

# 3rd party libs
from flask import g
from hpOneView.exceptions import HPOneViewException

# Modules own libs
from oneview_redfish_toolkit.api.errors import NOT_FOUND_ONEVIEW_ERRORS
from oneview_redfish_toolkit import client_session
from oneview_redfish_toolkit import config
from oneview_redfish_toolkit.config import PERFORMANCE_LOGGER_NAME

# Globals vars:
#   globals()['map_resources_ov']


def init_map_resources():
    globals()['map_resources_ov'] = OrderedDict()


def init_map_appliances():
    globals()['map_appliances_ov'] = OrderedDict()


def get_map_resources():
    return globals()['map_resources_ov']


def get_map_appliances():
    return globals()['map_appliances_ov']


def set_map_resources_entry(resource_id, ip_oneview):
    lock = threading.Lock()
    with lock:
        get_map_resources()[resource_id] = ip_oneview


def set_map_appliances_entry(ip_oneview, appliance_uuid):
    get_map_appliances()[ip_oneview] = appliance_uuid


def query_ov_client_by_resource(resource_id, resource, function,
                                *args, **kwargs):
    """Query resource on OneViews.

        Query specific resource ID on multiple OneViews.
        Look resource ID on cached map ResourceID->OneViewIP for query
        on specific cached OneView IP.
        If the resource ID is not cached yet it searchs on all OneViews.

        Returns:
            dict: OneView resource
    """
    # Get OneView's IP in the single OneView context or cached by resource ID
    ip_oneview = _get_single_oneview_ip() and \
        get_ov_ip_by_resource(resource_id)

    # If resource is not cached yet search in all OneViews
    if not ip_oneview:
        return search_resource_multiple_ov(resource, function, resource_id,
                                           *args, **kwargs)

    if _is_single_oneview_context():
        _set_single_oneview_ip(ip_oneview)

    ov_client = client_session.get_oneview_client(ip_oneview)

    return execute_query_ov_client(ov_client, resource, function,
                                   *args, **kwargs)


def get_ov_ip_by_resource(resource_id):
    """Get cached OneView's IP by resource ID"""
    map_resources = get_map_resources()

    return map_resources.get(resource_id)


def search_resource_multiple_ov(resource, function, resource_id,
                                *args, **kwargs):
    """Search resource on multiple OneViews

        Query resource on all OneViews.
        If it's looking for a specific resource:
            -Once resource is found it will cache the resource ID for the
                OneView's IP that was found;
            -If it is not found return NotFound exception.
        If it's looking for all resources(get_all):
            -Always query on all OneViews and return a list appended the
                results for all OneViews

        Args:
            resource: resource type (server_hardware)
            function: resource function name (get_all)
            resource_id: set only if it should look for a specific resource ID
            *args: original arguments for the OneView client query
            **kwargs: original keyword arguments for the OneView client query

        Returns:
            OneView resource(s)

        Exceptions:
            OneViewRedfishResourceNotFoundError: When resource was not found
            in any OneViews.

            HPOneViewException: When occur an error on any OneViews which is
            not an not found error.
    """
    result = []
    error_not_found = []

    # Loop in all OneView's IP
    for ov_ip in config.get_oneview_multiple_ips():

        ov_client = client_session.get_oneview_client(ov_ip)

        try:
            # Query resource on OneView
            expected_resource = \
                execute_query_ov_client(ov_client, resource, function,
                                        *args, **kwargs)

            if expected_resource:
                # If it's looking for a especific resource and was found
                if resource_id:
                    set_map_resources_entry(resource_id, ov_ip)
                    return expected_resource
                else:
                    # If it's looking for a resource list (get_all)
                    if isinstance(expected_resource, list):
                        result.extend(expected_resource)
                    else:
                        result.append(expected_resource)
        except HPOneViewException as e:
            # If get any error that is not a notFoundError
            if e.oneview_response["errorCode"] not in NOT_FOUND_ONEVIEW_ERRORS:
                logging.exception("Error while searching on multiple "
                                  "OneViews for Oneview {}: {}".
                                  format(ov_ip, e))
                raise e

            error_not_found.append(e)

    # If it's looking for a specific resource returns a NotFound exception
    if resource_id and error_not_found:
        raise error_not_found.pop()

    return result


def execute_query_ov_client(ov_client, resource, function, *args, **kwargs):
    """Execute query for resource on OneView client received as parameter"""
    ov_resource = getattr(ov_client, resource)
    ov_function = getattr(ov_resource, function)

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        start_time = time.time()

        try:
            result = ov_function(*args, **kwargs)
            return result
        except Exception as e:
            raise e
        finally:
            elapsed_time = time.time() - start_time

            g.elapsed_time_ov += elapsed_time

            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "Thread {} OneView request: {}.{}: {}".
                format(threading.get_ident(), resource,
                       function, elapsed_time))

    return ov_function(*args, **kwargs)


def set_single_oneview_context():
    """Set to use the same OneView IP in the same request"""
    g.single_oneview_context = True


def _is_single_oneview_context():
    """Check if it ot be used the same OneView IP on the request context"""
    return g.single_oneview_context


def _get_single_oneview_ip():
    """Get the same OneView's IP in request context"""
    if _is_single_oneview_context():
        return g.single_oneview_ip

    return None


def _set_single_oneview_ip(oneview_ip):
    """Set OneView's IP to be used in the same request context"""
    if not g.single_oneview_ip:
        g.single_oneview_ip = oneview_ip
