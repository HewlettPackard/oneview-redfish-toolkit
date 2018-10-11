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
from oneview_redfish_toolkit.config import ONEVIEW_SDK_LOGGER_NAME
from oneview_redfish_toolkit.config import PERFORMANCE_LOGGER_NAME
from oneview_redfish_toolkit import single_oneview_context as single

# Globals vars:
#   globals()['map_resources_ov']


lock = threading.Lock()


def init_map_resources():
    """Initialize cached resources map"""
    globals()['map_resources_ov'] = OrderedDict()


def init_map_appliances():
    """Initialize cached appliances map"""
    globals()['map_appliances_ov'] = OrderedDict()


def get_map_resources():
    """Get cached resources map"""
    return globals()['map_resources_ov']


def get_map_appliances():
    """Get cached appliances map"""
    return globals()['map_appliances_ov']


def set_map_resources_entry(resource_id, ip_oneview):
    """Set new cached resource"""
    with lock:
        get_map_resources()[resource_id] = ip_oneview


def cleanup_map_resources_entry(resource_id):
    with lock:
        if resource_id in get_map_resources().keys():
            del get_map_resources()[resource_id]


def set_map_appliances_entry(ip_oneview, appliance_uuid):
    """Set new cached appliance"""
    get_map_appliances()[ip_oneview] = appliance_uuid


def query_ov_client_by_resource(resource_id, resource, function,
                                *args, **kwargs):
    """Query resource on OneViews.

        Query specific resource ID on multiple OneViews.
        Look resource ID on cached map ResourceID->OneViewIP for query
        on specific cached OneView IP.
        If the resource ID is not cached yet it searches on all OneViews.

        Returns:
            dict: OneView resource
    """
    # Get OneView's IP in the single OneView context
    single_oneview_ip = single.is_single_oneview_context() and \
        single.get_single_oneview_ip()
    # Get OneView's IP for cached resource ID
    cached_oneview_ip = get_ov_ip_by_resource(resource_id)

    # Get OneView's IP in the single OneView context or cached by resource ID
    ip_oneview = single_oneview_ip or cached_oneview_ip

    # If resource is not cached yet search in all OneViews
    if not ip_oneview:
        return search_resource_multiple_ov(resource, function, resource_id,
                                           None, *args, **kwargs)

    # If it's Single Oneview context and no IP is saved on context yet
    if single.is_single_oneview_context() and not single_oneview_ip:
        single.set_single_oneview_ip(ip_oneview)

    ov_client = client_session.get_oneview_client(ip_oneview)
    try:
        resp = execute_query_ov_client(ov_client, resource, function,
                                       *args, **kwargs)
    except HPOneViewException as e:
        if e.oneview_response["errorCode"] not in NOT_FOUND_ONEVIEW_ERRORS:
            raise

        cleanup_map_resources_entry(resource_id)
        ov_ips = config.get_oneview_multiple_ips()
        ov_ips.remove(ip_oneview)  # just search in the other ips

        if not ov_ips:
            raise

        return search_resource_multiple_ov(resource, function,
                                           resource_id,
                                           ov_ips, *args,
                                           **kwargs)

    # If it's on Single OneView Context and the resource is not
    # mapped to an OneView IP, then we update cache in advance for
    # future requests for this resource
    if single_oneview_ip and not cached_oneview_ip:
        set_map_resources_entry(resource_id, single_oneview_ip)

    return resp


def get_ov_ip_by_resource(resource_id):
    """Get cached OneView's IP by resource ID"""
    map_resources = get_map_resources()

    return map_resources.get(resource_id)


def search_resource_multiple_ov(resource, function, resource_id, ov_ips,
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
            ov_ips: List of Oneview IPs to search for the resource.
                If None is passed, it will search in all IPs based on the
                toolkit configuration.
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
    single_oneview_ip = single.is_single_oneview_context() and \
        single.get_single_oneview_ip()

    # If it's on Single Oneview Context and there is already an OneView IP
    # on the context, then uses it. If not search on All OneViews
    if not ov_ips and single_oneview_ip:
        list_ov_ips = [single_oneview_ip]
    else:
        list_ov_ips = ov_ips or config.get_oneview_multiple_ips()

    # Loop in all OneView's IP
    for ov_ip in list_ov_ips:

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

                    # If it's SingleOneviewContext and there is no OneView IP
                    # on the context, then set OneView's IP on the context
                    if single.is_single_oneview_context() and \
                            not single_oneview_ip:
                        single.set_single_oneview_ip(ov_ip)

                    return expected_resource
                else:
                    # If it's looking for a resource list (get_all)
                    if isinstance(expected_resource, list):
                        result.extend(expected_resource)
                    else:
                        result.append(expected_resource)
        except HPOneViewException as exception:
            # If get any error that is not a notFoundError
            if exception.oneview_response["errorCode"] not in \
                    NOT_FOUND_ONEVIEW_ERRORS:
                logging.exception("Error while searching on multiple "
                                  "OneViews for Oneview {}: {}".
                                  format(ov_ip, exception))
                raise exception

            error_not_found.append(exception)

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
        host = ov_client.connection.get_host()

        try:
            result = ov_function(*args, **kwargs)
            msg = "Request to Oneview '%s' calling '%s.%s' with args %s " \
                  "and kwargs %s. Result: %s"
            logging.getLogger(ONEVIEW_SDK_LOGGER_NAME).debug(msg, host,
                                                             resource,
                                                             function, args,
                                                             kwargs, result)
            return result
        finally:
            elapsed_time = time.time() - start_time

            g.elapsed_time_ov += elapsed_time

            logging.getLogger(PERFORMANCE_LOGGER_NAME).debug(
                "Request to Oneview '%s' calling '%s.%s': %s",
                host, resource, function, elapsed_time)

    return ov_function(*args, **kwargs)
