[![Waffle.io - Columns and their card count](https://badge.waffle.io/HewlettPackard/oneview-redfish-toolkit.svg?columns=Ready,In%20Progress,Under%20Review)](https://waffle.io/HewlettPackard/oneview-redfish-toolkit) [![Build Status](https://travis-ci.org/HewlettPackard/oneview-redfish-toolkit.svg?branch=master)](https://travis-ci.org/HewlettPackard/oneview-redfish-toolkit) [![Coverage Status](https://coveralls.io/repos/github/HewlettPackard/oneview-redfish-toolkit/badge.svg?branch=master)](https://coveralls.io/github/HewlettPackard/oneview-redfish-toolkit?branch=master)

# HPE OneView Redfish Toolkit

This toolkit provides a REST service to answer [DMTF's Redfish](https://www.dmtf.org/standards/redfish) compliant requests by querying HPE OneView.

HPE OneView is a fresh approach to converged infrastructure management, inspired by the way you expect to work, with a single integrated view of your IT infrastructure.

DMTF's Redfish is an open industry standard specification and schema that specifies a RESTful interface and utilizes JSON and OData to help customers integrate solutions within their existing tool chains.



# Getting started

## Requirements

* **To install the application:**
  * Ubuntu 16.04 (standard server install works fine)
  * Python >=3.5
  * pip >=18.1
  * setuptools >=40.6.3
  * OpenSSL >= 1.0.2g
  * Internet connectivity
 * **To run the application (and make it useful):**
   * HPE OneView 4.0 or later

## Dependencies
All service dependencies (besides the ones listed under requirements above) will be automatically downloaded and installed as part of installing the service.
A full list of dependencies is available at [requirements.txt](requirements.txt) file

## Installing the application

```bash
$ pip install oneview-redfish-toolkit
```

## Offline Installation
### Obtaining Oneview Redfish Toolkit and dependencies
You can download offline installer at [Releases page](https://github.com/HewlettPackard/oneview-redfish-toolkit/releases).
Or you can download the toolkit from PyPI running this command:
```bash
$ pip download oneview-redfish-toolkit
```
### Installation
Create Python 3.5 virtual environment and activate it:
```bash
$ python3.5 -m venv <virtual-environment-name>
$ source <virtual-environment-name>/bin/activate
```

Update pip and setuptools to the latest version:
```bash
$ pip install pip -U
$ pip install setuptools -U
```

Unzip oneview-redfish-toolkit-installer:
```bash
$ unzip <oneview-redfish-toolkit-installer-0.4.0.zip>
```

Run pip install where the files are placed:
```bash
$ pip install <oneview-redfish-toolkit-installer-0.4.0>/*
```

## Running the application

The first time the application is run, it will create all the needed configuration files under user's home directory. It will also prompt for the OneView IP that you wish to connect to the redfish toolkit. This can either be a single IP address, or a comma seperated list of IP addresses.  The configuration is persisted in the  `redfish.conf`.

Below is an example run that will add two different OneView instances to the Redfish service:
```
$ oneview-redfish-toolkit
Welcome to oneview-redfish-toolkit. Please enter a comma separated list of OneView IPs you want to connect to.
Oneview IP(s): 192.168.3.100, 192.168.3.101
Using configuration file: /root/.config/oneview-redfish-toolkit/redfish.conf
Using logging configuration file: /root/.config/oneview-redfish-toolkit/logging.conf
oneview-redfish-toolkit service is now available at 0.0.0.0:5000
```

The following files will be created:

* $HOME/.config/oneview-redfish-toolkit/
  * redfish.conf
  * logging.conf
  * redfish.log
  * certs/

The `redfish.conf` and `logging.conf` are used  to customize the service, but generally, don't need to be modified. The `certs` directory is used to place the retrieved OneView certificates when the Event Service is enabled.




You can customize the configuration files created under the user directory, or if you want to use your own custom configuration files you can pass them as arguments. If no arguments are passed, the application will use the ones on user directory:

```bash
$ oneview-redfish-toolkit --config redfish.conf --log-config logging.conf
```



# Additional information about the toolkit

## Toolkit Configuration

The toolkit configuration resides on `redfish.conf` file. All required properties have default values that will work just fine. The only empty required property, OneView IP, will be prompted for user at the first execution and will update this file with inputed value. If OneView IP change or if you want add more OneViews you can manually update the property. In the same way you can edit the `redfish.conf` file to tuning other available properties.

You can check all properties listed below:

* `redfish` section
  * **indent_json**: whether JSON objects on answers are indented or not
  * **xml_prettify**: whether XML objects on answers are indented or not

  * **redfish_host**: the IP address where redfish service will listen to. Using `host = 0.0.0.0` means it will listen to all IP addresses.

  * **redfish_port**: the TCP port where redfish service will listen to

  * **authentication_mode**: can be `conf` or `session`.
    * **`conf`**: credentials from the conf file will be used for the requests. The toolkit will handle authentication with OneView internally. This configuration is the only mode that supports [Event Service](#event-service-notes) and it's recommended for demo purposes only.
    * **`session`**: the Redfish client must create a session and use the generated `x-auth-token` for the requests. For more details please check Session Management section.

* `redfish-composition` section
  * **PowerOffServerOnCompose**: enable or disable power off the server on composition. The default value used is **ForceOff** - an immediate (hard) shutdown. If not specified (blank value) no power off action will be performed.
  * **PowerOffServerOnDecompose**: enable or disable power off the server on decomposing a system. The default value used is **ForceOff** - an immediate (hard) shutdown. If not specified (blank value) no power off action will be performed. Other option can be **GracefulShutdown** - a normal (soft) power off.

* `oneview_config` section

  * **ip**: HPE OneView's IP/FQDN address or comma separated list of OneView's IP/FQDN address for multiple instances.
  
  Oneview Redfish Toolkit now also includes support for multiple OneView instances, allowing a single instance of the service manage more than one OneView instance instead of instantiating a new service for each HPE OneView that is part of the solution. It simplifies for the Redfish client that does not need to handle multiple connections to the Redfish services.

* `credentials` section

  * **username**: HPE OneView's username
  
  * **password**: HPE OneView's password

  * **authLoginDomain**: HPE OneView's authentication login domain. If not set, defaults to "Local".

  Note: HPE OneView credentials are used only for authentication_mode set to "conf". They are stored in clear-text. Make sure only authorized users can access this file. When handling multiple OneView instances, make sure all instances have this username/password enabled.

* `event_service` section

  * **DeliveryRetryAttempts**: The value of this property shall be the number of retrys attempted for any given event to the subscription destination before the subscription is terminated.
  
  * **DeliveryRetryIntervalSeconds**: The value of this property shall be the interval in seconds between the retry attempts for any given event to the subscription destination.

* `ssl` section

  * **SSLType**: select one of the options below. The default value used is **adhoc**.
    * **disabled**: no SSL. Flask will be used as the web server.
    * **adhoc**: SSL is enabled with self-signed keys generated by the server every time you start the server. Flask will be used as the web server.
    * **self-signed**: SSL is enabled with a self-signed cert generated in the certs directory if no files named self-signed.crt and self-signed.key exists in that directory. This will create the certificates on the first run and every time you delete the files and restart the server. The directory **certs must** exist in the system root directory) certs (SSL is enabled with keys provided by user in the fields below). Cherrypy will be used as the web server unless the toolkit is initialized in development and debug mode (arguments set "--dev" and "--debug"). In this case, Flask will be used as the web server.
  
  * **SSLCertFile**: The user SSL cert file.

  * **SSLKeyFile**: The user SSL key file. Should not have a password.

* `ssl-cert-defaults` section: Defines the values used in the self-signed generated certificate

  * **countryName**: The name of the country. **Required!**
  
  * **stateOrProvinceName**: The name of the state or province. **Required!**

  * **localityName**: Name of the locality (city for example). **Required!**

  * **organizationName**: Name of the organization (company name for example). **Required!**
  
  * **organizationalUnitName**: Name of the organizational unit (department for example). **Required!**

  * **commonName**: FQDN of the server or it's IP address. If not provided will detect de default route IP and use it. **Optional.**
 
  * **emailAddress**: Email address to contact the responsible for this server/certificate. This is an optional information. Will not be added to certificate if not informed. **Optional.**

* `cherrypy_config` section: See advanced CherryPy configuration [here](http://docs.cherrypy.org/en/latest/index.html)

## Logging

Logging configuration can be found in `logging.conf` file. The provided configuration enables INFO level at both console and file output, which will generate a `redfish.log`, `redfish_performance.log` and `redfish_ov_data.log` files at `$HOME/.config/oneview-redfish-toolkit/`.

The application has two extended logs, where all logs will be created on the same directory `$HOME/.config/oneview-redfish-toolkit/`:

#### Performance logger

For each Redfish Toolkit API request the performance logger will log the elapsed time for each OneView SDK request triggered, the amount elapsed time for all OneView SDK requests, the overhead toolkit process elapsed time and the total elapsed time for the Redfish Toolkit API request. So we can monitoring the OneView performance and the redfish toolkit performance as well. It will be log on `redfish_performance.log` file once enabled on `logging.conf` by changing its level and the root log level as DEBUG. Log example:
```
2018-10-10 15:42:41,112 - perf - DEBUG   - Thread 139974930331392 - OneView request: server_profile_templates.get: 0.02929878234
2018-10-10 15:42:42,304 - perf - DEBUG   - Thread 139974930331392 - OneView request: server_hardware.get_all: 0.03278422355
2018-10-10 15:42:43,231 - perf - DEBUG   - Thread 139974930331392 - OneView request: server_hardware.get_all:  0.03367638587
2018-10-10 15:42:43,291 - perf - DEBUG   - Thread 139974930331392 - OneView process: 0.09575939176
2018-10-10 15:42:43,291 - perf - DEBUG   - Thread 139974930331392 - Redfish process: 0.01273488998413086
2018-10-10 15:42:43,294 - perf - DEBUG   - Thread 139974930331392 - Total process: 0.10849428174
```

#### OneView Data logger

The OneView data logger will log the result for each OneView SDK request triggered. So we can check OneView data retrieved for each OneView SDK request. It will be log on `redfish_ov_data.log` file once enabled on `logging.conf` by changing its level and the root log level to DEBUG. Log example:
```
2018-10-10 15:42:43,230 - ovData - DEBUG - Thread 139974930331392 - Request to Oneview 'oneview.net', calling 'server_hardware.get_all' with args () and kwargs {}. Result: []
```


#### Enabling loggers

You can enable loggers `Performance`, `OneView Data` and others by setting its level and root logger level as DEBUG on the `logging.conf` file. For example:

```
[logger_root]
level=DEBUG

[logger_performance]
propagate=0
level=DEBUG
...
```
You can customize extended logs to have default entry logs as well. To do this add the extended loggers handlers to the root logger:
```
[logger_root]
level=DEBUG
handlers=consoleHandler,defaultFileHandler,performanceFileHandler,oneviewDataFileHandler
```

### Development Environment

In order to run tests and documentation generation `tox` is also needed. General instructions on how to install are available [here](https://tox.readthedocs.io/en/latest/install.html).

We recommend to run inside a virtual environment. You can create one running:

```bash
$ virtualenv env_name_you_choose -p python3.5 # to create a Python3.5 environment, for example
$ source env_name_you_choose/bin/activate # load the environment
```

Once the environment is loaded, download and uncompress the latest version from [releases page](https://github.com/HewlettPackard/oneview-redfish-toolkit/releases), or clone current development version running:

```bash
$ git clone https://github.com/HewlettPackard/oneview-redfish-toolkit.git
```

Then, proceed with:

```bash
$ cd oneview-redfish-toolkit # enter the service folder
# edit redfish.conf
$ pip install -r requirements.txt # to install all requirements into the virtual environment
$ ./run.sh    # to launch the service
```

## SDK Documentation

The latest version of the SDK documentation can be found in the [SDK Documentation section](https://hewlettpackard.github.io/oneview-redfish-toolkit/index.html).

> Note: This documentation has been manually updated following the steps found [here](https://github.com/HewlettPackard/python-hpOneView/blob/master/deploy.sh).

## Session Management

As specified in the Redfish spec, the endpoints `/redfish` and `/redfish/v1` can be accessed unauthenticated, also POST to Sessions Collection (that's how a Redfish session can be established).

To create a Redfish session, the redfish client must authenticate himself using his own username and password sending a post request to `/redfish/v1/SessionService/Sessions`. Since current toolkit implementation delegates the session management to OneView, the Redfish client must pass a valid OneView user and password:

```bash
curl -i -X POST \
  -H "Content-Type:application/json" \
  https://<ip>:5000/redfish/v1/SessionService/Sessions \
  -d '{"UserName": "administrator", "Password": "password"}'
```
One of the headers in the response is `X-Auth-Token` that should be send for all subsequent requests:

```bash
curl -X GET \
  -H "X-Auth-Token: NzQ8ODI6MTcxOTkxRdvdtE-HaNeFgkoylkaQVA3l1uIsHxQ7" \
  https://<ip>:5000/redfish/v1/Systems
```
When handling multiple OneView instances, make sure all instances have this username/password enabled.


## Event Service notes

Current implementation follows Redfish specification [DSP0266 version 1.5.0](https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.5.0.pdf). Event Service works only when authentication_mode is set to `conf` and does not support multiple OneView instances, hence it's not production ready. As it connects directly to HPE OneView SCMB, the toolkit will request OneView to generate SCMB certs and download the certs to the correct location. The certs file are: **oneview\_ca**: OneView's CA cert file located at: `certs/oneview_ca.pem`. **scmb\_cert**: OneView's SCMB Client cert file located at: `certs/oneview_scmb.pem`. **scmb\_key**: OneView's SCMB Client key file located at: `certs/oneview_scmb.key`

> In order to integrate properly with OneView, the OneView API 300 is required to be supported by OneView instance.

Only alerts and events related to enclosures, racks and server hardware are being monitored and will generate the following Redfish events: ResourceAdded, ResourceUpdated and ResourceRemoved.

## Composition Service

Current implementation follows Redfish specification [DSP2050 version 1.0.0](https://www.dmtf.org/sites/default/files/standards/documents/DSP2050_1.0.0.pdf) and does not use any OEM (vendor specific) attributes. One of the biggest challenges of adding composability support was to identify what type of Resource Blocks that should be available since full composability is not available due to limitations in the current specification. A first approach leveraging OneView server profile templates was proposed and evaluated with Redfish authors. With this proposal each OneView server profile template maps to Redfish Resource Zones that may list three types of resource blocks:
*	**Storage Resource Block**: each SAS drive from drive enclosures is mapped for a specific Resource Zone if the SAS storage controller is present in the server profile template. This block presents information about CapacityBytes, Protocol, and MediaType. Other storage types such as DAS and SAN disk are out of scope.
*	**Network Resource Block**: all connections (network and network sets) specified in the server profile template are mapped to Ethernet interfaces that are part of a Network Resource Block. This block presents information about network name, speedMbps, and VLANs.
*	**Computer System Resource Block**: each server that matches the server hardware type in the server profile template (Resource Zone) is mapped as a Computer System Resource Block. This block presents information about Processor (Model, MaxSpeedMHz, TotalCores) and Memory. The OneView Redfish service is responsible for making sure to list only Computer System Resource Blocks and Storage Resource Blocks that can be composed (located in the same Enclosure) for a specific Resource Zone. This is a different model than OneView, so extra validation was implemented rather than relying on the OneView server profile API directly.

On a Compose request, the Redfish client must select one Computer System Resource Block, one Network Resource Block, and as many Storage Resource Blocks as desired from the available Resource Blocks on the selected Resource Zone. The required attributes in the compose request are specified in the Capabilities Object. A server profile will be created leveraging the server profile template as identified in the POST request. Each Storage Resource Block (SAS drive) will be configured as external logical JBOD (logical drives are out of scope).

**Important**: To have the Composition Service functional, the administrator must create OneView server profile templates in advance. To allow Storage Resource Blocks in composition requests via the OneView Redfish service, the SAS storage controller should be configured, however, no drives should be added in the template (they will be assigned to the profile on the composition request).

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

## License

This project is licensed under the Apache License 2.0.
