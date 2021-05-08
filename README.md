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

## Running predefined test scripts
This program allows you to run a set of predefined commands for reproducible tests.

To do so, run the following command:
```console
foo@bar:~/brachyosaurus/src$ python brachy.py NEEDLE --test=YOUR_TEST_NAME_HERE
```

YOUR_TEST_NAME_HERE should be an entry in the ```src/config.ini``` file.

Tests need to be written in a uniform column wise manner, and will always run in the order of the following 6 predefined commands:

6 Predefined commands:

     - motor0test : List of steps this motor should take (regardless of current position)
     - motor0test : List of steps this motor should take
     - motor0test : List of steps this motor should take
     - motor0test : List of steps this motor should take
     - coords : List of tuples of the form (x, y), where the motors will move to in a synced fashion
     - sleep: List containing seconds, the program sleeps after each column for this amount.

The test inputs should be considered an 6 x N matrix, where N should be the number of positions you want to move to.

     - Run single motor: initialize all other motors and coords array to 1XN zero-array --> make wanted motor test array --> run test
     - Run multiple motors: initialize EITHER coords-array OR all 4 motor test arrays, set other array(s) to zero-array(s) --> run test
     - If you want to sleep until the user presses enter, add a 0 to the sleep column

### Example of Test Configuration
(See src/config.ini as well)

Here are some values of an example test
|                      |                                           |
|----------------------|-------------------------------------------|
| number_of_postions = | 4                                         |
| motor0test =         | [0, -20, 0, 0]                              |
| motor1test =         | [0, 0, 400, 1]                            |
| motor2test =         | [0, 100, 50, 300]                         |
| motor3test =         | [0, 0, 50, 400]                           |
| coords =             | [(0,0), (100, 100), (50, 50), (-50, 100)] |
| sleep =              | [0, 10, 0, 20]                            |

In this test, 4 iterations of positions will be ran.
The first column contains all zeroes, so will do nothing, and asks the user to press enter to continue (since sleep = 0)
Then the second position will be ran:
motor0 will move backwards with 20 steps. motor1 will do nothing. motor2 will move 100 steps forward. motor3 will do nothing. then the motors will move to position (100, 100) synced. The program then sleeps for 10 seconds, before moving onto iteration (position) 3. And so on...

## Authors
Team members:

     - Florens Helfferich   (4607155) F.J.Helfferich@student.tudelft.nl
     - Bram Pronk           (4613066) I.B.pronk@student.tudelft.nl
     
The project is guided by:

     - Martijn de Vries   
     - John van den Dobbelsteen     

## Licensing
This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE) for details
