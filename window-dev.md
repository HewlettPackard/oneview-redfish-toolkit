# Windows development environment setup

Follow the steps below to build a development environment on a Windows machine

* Install git
* Install python 3.5+ from python.org
* clone the project:

    `git clone https://HewlettPackard/oneview-redfish-toolkit`
* Access project directory:

    `cd oneview-redfish-toolkit`
* Create a virtual environment(venv):
    `py -m venv .venv`

    **NOTE:** `.venv` is the directory of the virtual environment. You can name it whatever you like, given it's not an existing directory in the project.
* Activate the virtual env:

    `./venv/scripts/activate`

    **NOTE:** this may trigger a security error. If you get an error regarding script policy you can pass that by issuing the command below:

    `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

    **NOTE:** in `.\venv\Scripts\` there are 3 activation scripts.
    * activate
    * activate.bat
    * activate.ps1

    The `activate` script checks if you are using **Windows command prompt** (`cmd`) or **Windows PowerShell**. If the first it then calls `activate.bat` if the later it calls `activate.ps1`. It's been reported that calling `activate` on **Windows 7 does not activate** the virtual environment. If you have this problem please call the proper script for your shell. On Windows 10, activate worked fine on both, **command** and **powershell**

    **NOTE:** to check inf you environment is active you will have`(.venv)` prepended to your prompt. The prepended string will be whatever you named you virtual env directory. See a example below:

    `(.venv)C:\MyProjects\oneview-redfish-toolkit> `

* Install the project and dependencies in the venv

    `pip install -e .`
* Edit the configuration file `redfish.conf` and setup the OneView credentials
* Starting the service:

    `./run.cmd`
* Runinng tests

    `py -m unittest`
* Runing pep8 check

    `py -m flake8`

