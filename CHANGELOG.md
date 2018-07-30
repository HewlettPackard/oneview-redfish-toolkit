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
 - #273 Create Installer
 - #237 Implement base CollectionCapabilities: "@Redfish.CollectionCapabilities" in the ResourceZone
 - #260 Create a ResourceZone for each Server Profile Template
 - #250 Implement ResourceBlock for Server Hardware
 - #276 Refactoring: create a base blueprint class
 - #264 Implement DELETE to delete a composed resource
 - #300 Include Storage Resource Blocks into Resource Blocks collection
 - #261 Implement Network Resource Block
 - #298 Include Network Resource Blocks into Resource Blocks collection
 - #293 Implement Storage ResourceBlock
 - #307 Add support for Processor resource in ComputerSystem
 - #262 Implement Capabilities endpoint
 - #295 Update Systems collection
 - #311 Resource Zone: update link to CapabilitiesObject
 - #329 Fix count on Computer System Collection
 - #339 Network Resource Block: add support for network sets
 - #299 Include Storage resource blocks in a Resource Zone
 - #309 Storage Resource Blocks in a Zone should be available only if storage controller is configured
 - #270 Implement ComputerSystem for a composed resource
 - #294 Include Network resource blocks in a Resource Zone
 - #335 Reset action to a System is not working properly
 - #317 Add support for Actions/Chassis.Reset in the Chassis for Server Hardware
 - #271 Implement "@Redfish.CollectionCapabilities" in the Systems collection
 - #337 Include information about Storage and Network for a Composed System
 - #339 Network Resource Block: add support for network sets
 - #341 Composed system: update NetworkInterfaces
 - #349 Refactor Redfish.conf
 - #263 Implement POST to create a composed resource
 - #340 Composed System: Add ResourceBlocks in the Links
 - #308 Update Links in the Storage Resource Block
 - #350 Refactor odata.type
 - #357 Set API version 500 for Event Service (workaround)

# New Redfish resources
 - Event Service
 - Event Subscription
 - Event Destination Collection
 - Event Destination
 - Event
 - Message
 - Composition Service
 - Resource Block Collection
 - Zone
 - Zone Collection
 - Collection Capabilities
 - Resource Block
 - Ethernet Interface Collection
 - Ethernet Interface
 - VLan Network Interface
 - VLan Network Interface Collection
 - Computer System (Composed scenario)
 - Storage Collection
 - Drive
 - Computer System Resource Block
 - Processor Collection
 - Processor
 - Storage Resource Block
 - Network Resource Block


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
 - Network Interface Collection
 - Network Interface
 - Network Adapter Collection
 - Network Adapter
 - Network Port Collection
 - Network Port
 - Network Device Function Collection
 - Network Device Function
 - Session Service
 - Session


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
 - Computer System collection
 - Computer System
 - Computer System (Boot, Processor and Memory mappings)
 - Chassis collection
 - Chassis
 - Thermal mappings for Chassis
 - Manager collection
 - Manager
 - Error responses
