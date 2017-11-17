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
