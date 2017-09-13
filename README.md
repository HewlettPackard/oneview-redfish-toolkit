[![Stories in Ready](https://badge.waffle.io/HewlettPackard/oneview-redfish-toolkit.png?label=ready&title=Ready)](http://waffle.io/HewlettPackard/oneview-redfish-toolkit) [![Build Status](https://travis-ci.org/HewlettPackard/oneview-redfish-toolkit.svg?branch=master)](https://travis-ci.org/HewlettPackard/oneview-redfish-toolkit)

# HPE OneView Redfish Toolkit

This toolkit provides a REST service to answer DMTF's Redfish compliant requests by querying HPE OneView.

HPE OneView is a fresh approach to converged infrastructure management, inspired by the way you expect to work, with a single integrated view of your IT infrastructure.

DMTF's Redfish is an open industry standard specification and schema that specifies a RESTful interface and utilizes JSON and OData to help customers integrate solutions within their existing tool chains.

## Installation

### From source

In a developement environment:

```bash
$ git clone https://github.com/HewlettPackard/oneview-redfish-toolkit.git
$ cd oneview-redfish-toolkit
$ tox -epy35 --notest  # create an environment with all dependencies
$ source .tox/py35/bin/activate # load the created environment
$ python run.py    # to launch the service
```

Or in a production environment:

```bash
$ git clone https://github.com/HewlettPackard/oneview-redfish-toolkit.git
$ cd oneview-redfish-toolkit
$ sudo pip install -r requirements.txt  # install all dependencies
$ python run.py    # to launch the service
```

## Redfish API Implementation

A status of the Redfish standand covered by the implemented service is available at [Wiki section](https://github.com/HewlettPackard/oneview-redfish-toolkit/wiki/Redfish-Implementation-Status).

## SDK Documentation

The latest version of the SDK documentation can be found in the [SDK Documentation section] (https://hewlettpackard.github.io/oneview-redfish-toolkit/index.html).

## Logging

Logging configuration can be found in `logging.ini` file. The provided configuration enables INFO level at both console and file output (which will generate a `redfish.log` file).

## Configuration

In order to start up oneview-redfish-toolkit service, there is some mandatory configuration at `redfish.ini` file to provide as explained below:

* `redfish` section

  * **schema_dir**: path to where DTMF's Redfish JSON schemas are stored
  
  * **indent_json**: whether JSON objects on answers are idented

* `oneview` section

  * **ip**: HPE OneView's IP or FQDN address
  
  * **api_version**: HPE OneView's version. Defaults to 300.

* `credentials` section

  * **username**: HPE OneView's username
  
  * **password**: HPE OneView's password

* `schemas` section

  * **ServiceRoot**: DTMF's Redfish JSON schema for the `Service Root` resource
  
  * **ChassisCollection**: DTMF's Redfish JSON schema for `Chassis` collections
  
  * **Chassis**: DTMF's Redfish JSON schema for `Chassis` resources
  
  * **ComputerSystemCollection**: DTMF's Redfish JSON schema for `Computer Systems` collections
  
  * **ComputerSystem**: DTMF's Redfish JSON schema for `Computer Systems` resources
  
  * **ManagerCollection**: DTMF's Redfish JSON schema for `Managers` collections
  
  * **Manager**: DTMF's Redfish JSON schema for `Manager` resources
  
  * **EventService**: DTMF's Redfish JSON schema for the `Event Service` resource
  
  * **EventDestination**: DTMF's Redfish JSON schema for `Event Destination` resources
  
  * **Event**: DTMF's Redfish JSON schema for `Event` objects

Note: HPE OneView' credentials are stred in clear-text. Make sure only authorized users can access this file.

## Contributing

You know the drill. Fork it, branch it, change it, commit it, and pull-request it. We are passionate about improving this project, and are glad to accept help to make it better. However, keep the following in mind:

We reserve the right to reject changes that we feel do not fit the scope of this project. For feature additions, please open an issue to discuss your ideas before doing the work.

## Feature Requests

If you have a need not being met by the current implementation, please let us know (via a new issue). This feedback is crucial for us to deliver a useful product. Do not assume that we have already thought of everything, because we assure you that is not the case.

## Testing

We have already packaged everything you need to do to verify if the code is passing the tests. The tox script wraps the unit tests execution against Python 3, flake8 validation, and the test coverage report generation.

Run the following command:

```
$ tox
```
