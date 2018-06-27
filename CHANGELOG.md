# 0.3.0 (unreleased)

# Bug fixes & Enhancements
 - #216 Implement GET EventService
 - #217 Implement GET SubscriptionCollection
 - #218 Implement POST Subscription
 - #221 Implement GET Subscription
 - #222 Open scmb connection
 - #225 Fix NetworkInterface URL in NetworkInterfaceCollection
 - #227 Implements DELETE Subscription
 - #243 Add info about session management (README)
 - #230 Check missing schemas from local repo
 - #236 Flask running in debug mode
 - #232 Implement CompositionService
 - #201 How are HPE OneView event types structured?
 - #214 Subscribe to each EventType
 - #215 Add TestEvent Action
 - #249 Redfish Events notification
 - #233 Implement ResourceBlocks
 - #234 Implement ResourceZones
 - #259 Add ResourceBlocks for each Server Profile Template in the ResourceBlocks collection
 - #258 Check OneView availability
 - #237 Implement base CollectionCapabilities: "@Redfish.CollectionCapabilities" in the ResourceZone
 - #260 Create a ResourceZone for each Server Profile Template
 - #250 Implement ResourceBlock for Server Hardware
 - #300 Include Storage Resource Blocks into Resource Blocks collection
 - #261 Implement Network Resource Block
 - #298 Include Network Resource Blocks into Resource Blocks collection
 - #293 Implement Storage ResourceBlock
 - #307 Add support for Processor resource in ComputerSystem

# New Redfish resources
 - EventService
 - EventSubscription
 - EventDestinationCollection
 - EventDestination
 - CompositionService
 - ResourceBlockCollection
 - Zone
 - ZoneCollection
 - ResourceBlock
 - EthernetInterface
 - ProcessorCollection
 - Processor


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
