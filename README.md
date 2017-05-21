# Chaos-Productivity-Tool

## Description
Chaos is a tiny but powerful tool developed under linux to help you be more productive. It implements a task list, timer, alarms, stopwatch with lap times and a countdown to date widget with a beautiful and clean interface. When you quit the application it will save all your non-volatile data such as tasks, alarms and countdown date (if one was set) so that you never lose your important data. For a full preview of the app have a look at the screenshots in the corresponding folder.

![Timer Tab](/screenshots/timer.png)

## Requirements
Chaos is written using python and PyQt4 and requires the following packages to be pre-instaled:
- python-pyqt4 (used to develop the user interface)
- python-pygame (used to play the alarm and timer sounds)

> These requirements can be installed by running the following command in terminal:

`sudo apt-get install python-pyqt4 python-pygame`

## Installation
After cloning this repository and satisfying the aforementioned requirements you can run the application by opening a terminal in the cloned directory and typing:

`./Chaos.sh` or in some linux distributions `sudo ./Chaos.sh` .

Alternatively you can run it with your python interpreter with `python main.py`

## Compatibility
This application has been tested under Linux Mint, Elementary OS and Ubuntu, however, certain differences in appearance can be expected across different linux distributions.
