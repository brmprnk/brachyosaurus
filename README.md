# brachyosaurus
![2](https://d1rkab7tlqy5f1.cloudfront.net/Admin/Julie/TUD.png) <!-- .element height="50%" width="100%" -->


[![Python 3](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org/download/releases/3.0/) 
![GitHub license](https://img.shields.io/github/license/haccer/tweep.svg)

WIP: This project controls four linear motors in order to appropriately steer and bend a bendable needle.

## Getting Started
<!---

This section should contain installation, testing, and running instructions for people who want to get started with the project. 

- These instructions should work on a clean system.
- These instructions should work without having to install an IDE.
- You can specify that the user should have a certain operating system.

--->
Clone or download the project to your local machine.

This Program runs in Python 3. We are certain the program supports Python 3.8.5, use an older Python 3 version at own risk. Python2 will not run.


## Required Packages and Installation
Recommended way to install is using pip.
Example command would be:
```console
foo@bar:~$ pip install labjack-ljm
```
     
- labjack-ljm [(Link)](https://github.com/labjack/labjack-ljm-python)
- pyfirmata
- numpy
- argparse
- pygame
- opencv-python

When all is installed, what remains is installing the labjack software from: [(LabJack)](https://labjack.com/support/software/applications/t-series/kipling)

## Running the program
After installing all required packages, note the run options in the project's main file: src/brachy.py

Ensure the Arduino, Labjack and an input source (keyboard or Xbox One Controller) are connected via USB to the running machine.
Note the COMPORT where the Arduino is connected, this needs to be passed to the program.
Make sure the circuitboard is connected to a power source with a voltage of ~9V.

Navigate in the command line or terminal to the src folder, and run the following command:
```console
foo@bar:~/brachyosaurus/src$ python brachy.py
```
All helpful commands will be listed. An example of running the needle module would be:
```console
foo@bar:~/brachyosaurus/src$ python brachy.py NEEDLE --comport=COM4 --sensitivity=0.2
```

## Authors
Team members:

     - Florens Helfferich   (4607155) F.J.Helfferich@student.tudelft.nl
     - Bram Pronk           (4613066) I.B.pronk@student.tudelft.nl
     
The project is guided by:

     - Martijn de Vries   
     - John van den Dobbelsteen     

## Licensing
This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE) for details
