MATLAB - LJM .NET examples for Windows
12/04/2017
support@labjack.com


This package contains MATLAB example scripts that demonstrate LabJack T7 and T4
usage using the MATLAB .NET interface and LJM .NET assembly. Examples were last
tested with MATLAB 9.1 (R2016b).


Requirements:

1. Windows operating system
2. MATLAB with .NET interface support. Version 7.8 (R2009a) or newer.
3. LJM driver and .NET assembly. Both are provided by the Windows installer:

   https://labjack.com/support/software/installers


Getting Started:

First make sure that you have fulfilled the requirements and have extracted the
example scripts somewhere on your computer.

A simple way to get the example scripts running in MATLAB is to navigate to the
extracted MATLAB_LJM folder in the "Current Folder" toolbar. Using the toolbar
you can "Add to Path" MATLAB_LJM folders and scripts, and open and run scripts.
Alternatively, you can use "File->Set Path" to add the MATLAB_LJM and subfolders
to the path.

Once added to the path, you can run scripts by name in MATLAB. For example:

>> eReadNames

Note that the above instructions are from using MATLAB 7.9 (R2009b), and may
differ in newer MATLAB versions. All example scripts use the showDeviceInfo
and showErrorMessage function scripts.


Using the MATLAB .NET interface with the LJM .NET assembly:

To use the LJM .NET assembly in MATLAB use the NET.addAssembly method and
specify 'LabJack.LJM'.

>> ljmAsm = NET.addAssembly('LabJack.LJM')

That will make the LJM classes accessible in MATLAB. Methods, classes and enums
are in the LabJack.LJM class. Information on the LJM .NET assembly can be found
in the returned .NET assembly object from the NET.addAssembly call. For example,
to get a list of classes type the following:

>> disp(ljmAsm.Classes)

To get information on the LJM .NET class methods under MATLAB use the
methodsview call.

>> methodsview(LabJack.LJM)

To get a list of the LabJack.LJM.CONSTANTS class properties/constants, perform
the following calls:

>> t = ljmAsm.AssemblyHandle.GetType('LabJack.LJM+CONSTANTS')
>> LJM_CONSTANTS = System.Activator.CreateInstance(t)
>> disp(LJM_CONSTANTS)

The example scripts will provide additional help on MATLAB code and usage.


Documentation:

General LJM library documentation can be found here:

https://labjack.com/support/software/api/ljm

All Modbus register addresses are documented here:

https://labjack.com/support/software/api/modbus/modbus-map

T7 and T4 documentation can be found here:

https://labjack.com/support/datasheets/t-series


Licenses:

Provided LabJack example source code in this package are licensed under MIT
X11. See the LICENSE.txt file for details.
