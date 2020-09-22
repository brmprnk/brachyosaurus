%%% written by Arjan van Dijk, nov 2017. Used by Don Adrichem

%%% This function allows the user to set the Festo stage on the breathing
%%% phantom. 
%%% newfreq is set as 1.0 for 10 rpm; 1.2 for 12 rpm; 1.8 for 18 rpm and so
%%% on
%%% newamp is set as 10 for 20 mm amplitude, e.g. multiply newamp times 2

%%
% stroke liver is 11.89
% 
function MoveLiver(newfreq,newamp)

%Make the LJM .NET assembly visible in MATLAB
ljmAsm = NET.addAssembly('LabJack.LJM');

t = ljmAsm.AssemblyHandle.GetType('LabJack.LJM+CONSTANTS');

%creating an object to nested class LabJack.LJM.CONSTANTS
LJM_CONSTANTS = System.Activator.CreateInstance(t);

ljmHandle = 0;
try
    % Open first found LabJack
    [ljmError, ljmHandle] = LabJack.LJM.OpenS('ANY', 'USB', 'ANY', ljmHandle);
    
    showDeviceInfo(ljmHandle);
    
    %Setup and call eWriteAddress to write a value to the LabJack.
    f_address = 46000;  % USER_RAM0_F32 
    a_address = 46002;  % USER_RAM1_F32 
    dataType = LJM_CONSTANTS.FLOAT32;
    LabJack.LJM.eWriteAddress(ljmHandle, f_address, dataType, newfreq);
    LabJack.LJM.eWriteAddress(ljmHandle, a_address, dataType, newamp);
    
catch e
    showErrorMessage(e)
end

try
    % Close handle
    LabJack.LJM.Close(ljmHandle);
    disp('LabJack closed');
catch e
    showErrorMessage(e)
end

end

function showErrorMessage(e)
% showErrorMessage Displays the LJM or .NET error from a MATLAB exception.

if(isa(e, 'NET.NetException'))
    eNet = e.ExceptionObject;
    if(isa(eNet, 'LabJack.LJM.LJMException'))
        disp(['LJM Error: ' char(eNet.ToString())])
    else
        disp([char(class(eNet)) ': ' char(eNet.ToString())])
    end
end
disp(getReport(e))

end

function showDeviceInfo(handle)
% showDeviceInfo Displays the device's information based on the passed
% device handle.

[ljmError, deviceType, connType, serialNumber, ipAddress, port, maxBytesPerMB] = LabJack.LJM.GetHandleInfo(handle, 0, 0, 0, 0, 0, 0);
ipAddrStr = '';
[ljmError, ipAddrStr] = LabJack.LJM.NumberToIP(ipAddress, ipAddrStr);
disp(['Opened a LabJack with Device type: ' num2str(deviceType) ', Connection type: ' num2str(connType) ','])
disp(['Serial number: ' num2str(serialNumber) ', IP address: ' char(ipAddrStr)  ', Port: ' num2str(port) ','])
disp(['Max bytes per MB: ' num2str(maxBytesPerMB)])

end

