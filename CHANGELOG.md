# 0.3.0

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
 - #251 Modify Event Subscription URI
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
 - #344 Removing ExtendInfo from bad_request error
 - #271 Implement "@Redfish.CollectionCapabilities" in the Systems collection
 - #337 Include information about Storage and Network for a Composed System
 - #339 Network Resource Block: add support for network sets
 - #341 Composed system: update NetworkInterfaces
 - #353 Fixes "get Zone" when avaialable targets returns empty bays
 - #349 Refactor Redfish.conf
 - #263 Implement POST to create a composed resource
 - #340 Composed System: Add ResourceBlocks in the Links
 - #308 Update Links in the Storage Resource Block
 - #350 Refactor odata.type
 - #357 Set API version 500 for Event Service (workaround)
 - #361 Allows create properly a Composed System without Storage
 - #266 Redfish config file should have a list of OneView IPs
 - #355 Resource Blocks in a Zone should list all Computer System Resource Blocks that could be used in a composition and not just "Unused" ones
 - #373 Avoid redirection to GET when we call POST redfish/v1/Systems
 - #371 Storage Resource Block has Unused state even when should be Composed
 - #313 Resource Blocks in a Zone: update list based on the enclosure
 - #356 Resource Zones Collection: update list based on enclosure when storage controller is configured in the SPT
 - #267 Authentication for each request should be based on the REDFISH_SESSION_TOKEN defined during Redfish session creation
 - #368 Update GET capabilities object for the new ID
 - #369 Update Capabilities Objects references in the System Collection
 - #296 Update Status for Computer System Resource Block and for Composed System based on Oneview response
 - #378 Update references for Zones in Resource Blocks and in the request Body to create Composed System
 - #379 Update Status for Chassis based on OneView response
 - #382 Fix Storage for Composed System when there are no drives
 - #268 Redfish collection resources should return the list of resources from all OneView instances registered
 - #286 Refactoring unit tests
 - #393 Credentials should not be required in production mode
 - #396 Error on create new Composed System
 - #380 Update CompositionState of Computer System Resource Block
 - #231 Check updates on the implemented endpoints (new schema versions)
 - #375 Change POST to compose a system to return the new uuid as soon as profile uuid is available
 - #391 Zone name must be unique
 - #366 Concurrency for multiple OneView
 - #414 Conf mode is requiring auth token
 - #417 Request /redfish/v1/Systems list only Composed Systems (Server Profiles) without errors in Oneview
 - #392 ZoneCollection is listing Zones even for enclosures that do not have Drive Enclosure
 - #348 Change Oneview Redfish Toolkit to use CherryPy
 - #389 Update Links to ComputerSytems in the Chassis resource
 - #421 Add support for authLoginDomain in the Redfish.conf
 - #370 Use a label to save template_UUID instead of Description attribute in the server profile
 - #422 Save OneView Python SDK client for multiple requests
 - #387 Add support for Description in Composed system and Capabilities Object
 - #432 Log elapsed time for request in debug mode
 - #439 Fix unit tests for conf mode and client session tests
 - #407 create session id and when authorization fail, remove session (session id)
 - #408 Session collection and specific Session: list all session ids and a specific session
 - #441 Remove abandoned and expired sessions
 - #423 Power off the server on decompose request
 - #434 Power off the server on compose request
 - #445 Including cherrypy configs on redfish.conf
 - #448 Fix threading lock
 - #447 Log: add info about how many OV and Redfish resources
 - #433 Check performance for Storage Resource Block and Network Resource Block
 - #321 Review build dependencies
 - #409 Support for Delete Session
 - #297 Update Managers collection and Manager
 - #280 Empty collections should not return error message
 - #436 Certificates directory on production installation for conf mode
 - #458 Not found error should not return 500 on requests
 - #401 Change order of scmb certs generation
 - #428 Performance analysis
 - #438 Session Service and Event Service should be enabled according authentication mode
 - #472 Add SharingCapable attribute for Storage Resource Block
 - #471 Add SharingEnable attribute for Network Resource Block
 - #468 Improve error message for errors 500
 - #464 Improvement performance for multiple OneViews
 - #465 Update cache entry when resource moved to another OneView
 - #483 Missing Network Resource Block in a Zone when SPT has no connections
 - #484 Fix odata_id links for NetworkAdapterCollection and NetworkAdapter (api)
 - #480 Improve debug log
 - #478 Extend additional check for storage controller settings
 - #325 Package installation requirements

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
