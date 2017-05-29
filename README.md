# Chaos-Productivity-Tool

## Description
Chaos is a tiny but powerful tool developed under linux to help you be more productive. It implements a task list, timer, alarms, stopwatch with lap times and a countdown to date widget with a beautiful and clean interface. When you quit the application it will save all your non-volatile data such as tasks, alarms and countdown date (if one was set) so that you never lose your important data. For a full preview of the app have a look at the screenshots in the corresponding folder.

![Timer Tab](/screenshots/timer.png)

You can also check it out on [YouTube](https://youtu.be/GZdWcIfJl9U) 

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
This application has been tested under Linux Mint (18.1), Elementary OS (Loki) and Ubuntu (16.04), however, certain differences in appearance can be expected across different linux distributions.

## Update log
# 29th of May 2017
Following a user request, the following functionality was added to the app:
- Task deadlines. The user can now add a deadline to each task and will receive a notification when that task is due
- Task priority. The user can now specify a priority level for each task and thus change the colour of the task. The priority levels have been adopted from Steven Covey's book "The 7 Habits of Highly Effective People" and are as follows: Important and Urgent (red background), Important but not Urgent (orange background), Not Important but Urgent (green background), Not Important and not Urgent (blue background). More information on this book and Covey's priority system can be found [here](http://www.planetofsuccess.com/blog/2015/stephen-coveys-time-management-matrix-explained/).
- Important! - Tasks which are past their deadlines will not be loaded at startup. (I am open to elegant solutions for this problem)
