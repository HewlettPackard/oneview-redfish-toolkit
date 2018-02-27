# 0.3.0 (unreleased)

# Bug fixes & Enhancements
 - #216 Implement GET EventService
 - #217 Implement GET SubscriptionCollection
 - #218 Implement POST Subscription
 - #221 Implement GET Subscription
 - #222 Open scmb connection
 - #225 Fix NetworkInterface URL in NetworkInterfaceCollection
 - #227 Implements DELETE Subscription
 
# New Redfish resources
 - EventService
 - EventSubscription
 - EventDestinationCollection
 - EventDestination


# 0.2.0
# Notes
 - Check README for more information on the new authentication mode and
 the changes in configuration for self-signed certificates.

# Bug fixes & Enhancements
 - #159 Add support to OData-Version header
 - #162 Warn user when not using https with valid certificate
 - #163 Revert to https by default
 - #164 Generate a self-signed cert on first run
 - #169 New windows launcher script
 - #151 Enhances log messages with stack traces for debugging
 - #135 Perform schema validation with local resources
 - #184 Add config support to session based authentication 
 - #197 Fix schema loading when running on Windows
 - #198 Allow user to specify a different host ip address
 - #209 Fix wrong links in XML metadata
 
# New Redfish resources
 - Storage
 - Network Interface
 - NetworkAdapter
 - NetworkPort
 - NetworkDeviceFunction
 - SessionService/Sessions


# 0.1.2
# Bug fixes
This release fixes problems with service launcher.

# 0.1.1
#### Bug fixes
This release fixes problems when launching the service outside a python
virtual environment. It also reverts SSLType default value to 'adhoc'
as pointed in the README.

#### Notes
Installation requirements and instructions were updated to emphasize the
usage of Python 3.5 or later with virtual environment setup.


# 0.1.0
#### Notes
This is the first release of the OneView Redfish Toolkit. It is compatible
with HPE OneView Rest API version 300 or higher. Initial release supports
the following features:

#### Redfish features supported
 - Service Root
 - System collection
 - System
 - System (Boot, Processor and Memory mappings)
 - Chassis collection
 - Chassis
 - Thermal mappings for Chassis
 - Manager collection
 - Manager
 - Error responses
