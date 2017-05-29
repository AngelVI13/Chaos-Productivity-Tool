# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import time
import design  # imports the generated design code
import pygame # used to play sounds
import os


# used to translate the html markup for the countdown label
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class TaskHistoryPopup(QtGui.QWidget):
	def __init__(self, completed_tasks):
		QtGui.QWidget.__init__(self)
		self.completed_tasks = completed_tasks  # a list of completed tasks

		self.setWindowTitle("Task History")

		taskListLabel = QtGui.QLabel("Completed tasks")
		
		self.taskHistoryList = QtGui.QListWidget()
		self.taskHistoryList.resize(200,200)
		self.taskHistoryList.doubleClicked.connect(self.recover_task)

		for deadline, task in self.completed_tasks.items():
			self.taskHistoryList.addItem(task)

		recoverTaskBtn = QtGui.QPushButton("Recover Task")
		recoverTaskBtn.clicked.connect(self.recover_task)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(taskListLabel)
		layout.addWidget(self.taskHistoryList)
		layout.addWidget(recoverTaskBtn)
		self.setLayout(layout)


	def recover_task(self):
		task = self.taskHistoryList.currentItem().text()
		self.taskHistoryList.takeItem(self.taskHistoryList.currentRow())
		task_key = self.completed_tasks.keys()[self.completed_tasks.values().index(task)]
		self.completed_tasks.pop(task_key)  # removes the task from the completed list
		self.emit(QtCore.SIGNAL('recover_task(QString, QDateTime)'), task, task_key)


class AddAlarmPopup(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setWindowTitle("Add Alarm")

		alarmDescrLabel = QtGui.QLabel("Enter alarm description:")
		
		self.alarmDescription = QtGui.QLineEdit()

		self.now = QtCore.QDateTime.currentDateTime()  # gets current date time
		self.alarmDateTime = QtGui.QDateTimeEdit()
		self.alarmDateTime.setDateTime(self.now)  # sets alarm date time to current date time

		self.setAlarmBtn = QtGui.QPushButton('Set Alarm')
		self.setAlarmBtn.clicked.connect(self.set_alarm)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(alarmDescrLabel)
		layout.addWidget(self.alarmDescription)
		layout.addWidget(self.alarmDateTime)
		layout.addWidget(self.setAlarmBtn)
		
		self.setLayout(layout)


	def set_alarm(self):
		if self.alarmDescription.text() != '':
			if self.alarmDateTime.dateTime().toMSecsSinceEpoch() > self.now.toMSecsSinceEpoch():
				self.emit(QtCore.SIGNAL('add_alarm(QString, QDateTime)'), self.alarmDescription.text(), self.alarmDateTime.dateTime())
			else:
				QtGui.QMessageBox.warning(self, 'Error', 'Alarm time must be in the future!', QtGui.QMessageBox.Ok)
		else:
			QtGui.QMessageBox.warning(self, 'Error', 'Please enter an alarm description!', QtGui.QMessageBox.Ok)


class AddTaskPopup(QtGui.QWidget):
	def __init__(self, task=None, priority=None):
		QtGui.QWidget.__init__(self)
		self.task = task
		self.priority = priority
		self.setWindowTitle("Add Task")

		taskDescrLabel = QtGui.QLabel("Task description:")
		taskDeadlineLabel = QtGui.QLabel("Deadline:")
		taskPriorityLabel = QtGui.QLabel("Priority:")
		
		self.taskDescription = QtGui.QLineEdit()

		self.now = QtCore.QDateTime.currentDateTime()  # gets current date time
		self.taskDeadline = QtGui.QDateTimeEdit()
		self.taskDeadline.setDateTime(self.now)  # sets alarm date time to current date time

		self.priorityBox = QtGui.QComboBox(self)
		self.priorityBox.addItem('Important and Urgent')
		self.priorityBox.addItem('Important but not Urgent')
		self.priorityBox.addItem('Not Important but Urgent')
		self.priorityBox.addItem('Not Important and not Urgent')

		self.addTaskBtn = QtGui.QPushButton('Add Task')
		self.addTaskBtn.clicked.connect(self.add_task)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(taskDescrLabel)
		layout.addWidget(self.taskDescription)
		layout.addWidget(taskDeadlineLabel)
		layout.addWidget(self.taskDeadline)
		layout.addWidget(taskPriorityLabel)
		layout.addWidget(self.priorityBox)
		layout.addWidget(self.addTaskBtn)
		
		self.setLayout(layout)
		
		# if task data is suplied then this popup is used to edit a task
		if self.task is not None and self.priority is not None:
			self.setWindowTitle("Edit Task")
			self.addTaskBtn.setText('Recover Task')
			self.taskDescription.setText(task)
			priority_index = self.priorityBox.findText(priority)
			self.priorityBox.setCurrentIndex(priority_index)

	def add_task(self):
		if self.taskDescription.text() != '':
			if self.taskDeadline.dateTime().toMSecsSinceEpoch() > self.now.toMSecsSinceEpoch():
				self.emit(QtCore.SIGNAL('add_task(QString, QDateTime, QString)'), self.taskDescription.text(), self.taskDeadline.dateTime(), self.priorityBox.currentText())
			else:
				QtGui.QMessageBox.warning(self, 'Error', 'Task deadline must be in the future!', QtGui.QMessageBox.Ok)
		else:
			QtGui.QMessageBox.warning(self, 'Error', 'Please enter a task description!', QtGui.QMessageBox.Ok)


class countdownThread(QtCore.QThread):
	def __init__(self, countdown_sec):
		QtCore.QThread.__init__(self)
		self.countdown_sec = countdown_sec


	def __del__(self):
		self.wait()


	def run(self):
		# Wait for a sec and send a signal to update label
		while self.countdown_sec > 0:
			self.sleep(1)
			self.countdown_sec -= 1
			self.emit(QtCore.SIGNAL('update_label(int)'), self.countdown_sec)

		self.emit(QtCore.SIGNAL('timer_finished()'))


class stopwatchThread(QtCore.QThread):
	def __init__(self, running, milli_sec):
		QtCore.QThread.__init__(self)
		self.running = running
		self.milli_sec = milli_sec
		# self.connect(self.parent, QtCore.SIGNAL('stop_running()'), self.stop_running)


	def __del__(self):
		self.wait()


	def stop_running(self):
		self.running = False


	def run(self):
		# Wait for a sec and send a signal to update label
		while self.running is True:
			time.sleep(0.1)
			self.milli_sec += 100
			self.emit(QtCore.SIGNAL('update_stopwatch(int)'), self.milli_sec)


class TimerApp(QtGui.QMainWindow, design.Ui_MainWindow):
	countdown_sec = 60  # temp var used for countdown
	started = False  # state var
	paused = False  # state var
	task_dict = {}  # emty dict of current tasks
	completed_tasks = {}  # empty dict of completed tasks
	stopwatch_running = False  # state var
	milli_sec = 0  # initial stopwatch value
	lap_number = 1  # initial lap number
	lap_list = []  # empty list of lap times
	countdown_to_date = False  # state var
	alarm_set = False  # state var
	alarm_dict = {}  # empty alarm dictionary
	
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.setFixedSize(400,410)
		# timer buttons
		self.startBtn.clicked.connect(self.start_countdown)
		self.stopBtn.clicked.connect(self.reset_countdown)
		self.connect(self.timeEdit, QtCore.SIGNAL("timeChanged(QTime)"), self.update_label_signal)
		# task menu buttons
		self.addTask.clicked.connect(self.enter_task)
		self.taskHistoryBtn.clicked.connect(self.show_task_history)
		self.taskWidgetsVLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_3)
		# stopwatch buttons
		self.startBtn_2.clicked.connect(self.start_stopwatch)
		self.stopBtn_2.clicked.connect(self.stop_stopwatch)
		self.lapBtn.clicked.connect(self.take_lap_time)
		self.lapTimeVLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
		# countdown timer music engine
		pygame.mixer.init()  # initializing mixer engine
		# countdown to date
		self.now = QtCore.QDateTime.currentDateTime()  # gets current date time
		self.dateTimeEdit.setDateTime(self.now)  # sets the dateTimeEdit to now
		self.countdownStart.clicked.connect(self.start_countdown_to_date)
		self.tabWidget.currentChanged.connect(self.update_date_time_widget)
		# alarm
		self.addAlarmBtn.clicked.connect(self.set_alarm)
		self.alarmWidgetsVLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_2)

		# enable when updated to fit new task dict
		self.load_app_data()


	def closeEvent(self, evnt):
		# this method overrides the method called when the 'X' of the app is pressed
		choice = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure you would like to quit?',
			QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:
			self.save_app_data()
			# exits the application
			sys.exit()
		else:
			evnt.ignore()


	def save_app_data(self):
		# write non-volatile task data to file
		file = open('task_data.txt', 'w')

		for task in self.task_dict:
			task_deadline_date_time_str = task.toString()
			file.write(task_deadline_date_time_str + '|' + self.task_dict[task] + '\n')
		
		file.close()

		# write non-volatile task data to file
		file = open('alarm_data.txt', 'w')

		for alarm in self.alarm_dict:
			alarm_date_time_str = alarm.toString()
			file.write(alarm_date_time_str + '|' + self.alarm_dict[alarm] + '\n')
		
		file.close()

		# write non-volatile countdown data to file
		file = open('countdown_data.txt', 'w')

		countdown_date_time_str = self.dateTimeEdit.dateTime().toString()
		file.write(countdown_date_time_str + '\n')
	
		file.close()


	def load_app_data(self):
		# loads tasks data
		expired_tasks = 0  # counts the number of expired tasks
		task_data_filename = 'task_data.txt'
		if os.path.isfile(task_data_filename):
			file = open(task_data_filename, 'r')
			data = file.read().splitlines()  # removes end of line and newline chars
			if data:  # if data is not empty
				for task_row in data:
					task = task_row.split('|')
					task_deadline = QtCore.QDateTime.fromString(task[0])

					now = QtCore.QDateTime.currentDateTime()  # gets current time
					if task_deadline < now:  # does not add old alarms
						expired_tasks += 1
						continue

					# extract task description and priority from the saved file
					task_str = task[1].split(' until ')
					task_description = task_str[0].translate(None, "'")
					task_priority = task_str[1].split(' - ')[1]
					self.add_task(task_description, task_deadline, task_priority)

				# if some tasks were with expired deadlines and therefore not loaded - tell user
				if expired_tasks > 0:
					QtGui.QMessageBox.information(self, 'Warning', '%s task/s have been found to be past their deadline and were, therefore, deleted.' % expired_tasks,
					 QtGui.QMessageBox.Ok)

		# loads alarm data
		alarm_data_filename = 'alarm_data.txt'
		if os.path.isfile(alarm_data_filename):
			file = open(alarm_data_filename, 'r')
			data = file.read().splitlines()  # removes end of line and newline chars
			if data:  # if data is not empty
				for alarm_row in data:
					alarm = alarm_row.split('|')
					alarm_date_time = QtCore.QDateTime.fromString(alarm[0])
					alarm_description = alarm[1]

					now = QtCore.QDateTime.currentDateTime()  # updates current date time var
					if alarm_date_time < now:  # does not add old alarms
						continue
					self.create_alarm(alarm_description, alarm_date_time)

		# loads countdown to date data
		countdown_to_date_file = 'countdown_data.txt'
		if os.path.isfile(countdown_to_date_file):
			file = open(countdown_to_date_file, 'r')
			data = file.read().splitlines()  # removes end of line and newline chars
			if data:  # if data is not empty
				for date in data:
					countdown_date_time = QtCore.QDateTime.fromString(date)

					now = QtCore.QDateTime.currentDateTime()  # updates current date time var
					if countdown_date_time < now:  # does not add old alarms
						continue
					self.dateTimeEdit.setDateTime(countdown_date_time)
					self.start_countdown_to_date()


	def start_countdown(self):
		if self.started is False:
			self.started = True
			self.startBtn.setText('Pause')
			self.inputTimeSec = (self.timeEdit.time().minute()*60) + self.timeEdit.time().second()

			if self.paused is True:
				self.paused = False
				self.countdown_thread = countdownThread(self.countdown_sec)
			else:
				self.countdown_thread = countdownThread(self.inputTimeSec)
			self.connect(self.countdown_thread, QtCore.SIGNAL('update_label(int)'), self.update_label)
			self.connect(self.countdown_thread, QtCore.SIGNAL('timer_finished()'), self.timer_finished)
			self.countdown_thread.start()
		else:
			self.pause_countdown()


	def update_label(self, countdown_sec):
		self.countdown_sec = countdown_sec  # updates countdown_sec value
		duration_string = time.strftime("%M:%S", time.gmtime(countdown_sec))  # formats time to MM:SS
		self.timeLabel.setText(_translate("MainWindow", ("<html><head/><body><p align=\"center\"><span style=\" font-size:72pt; font-weight:600;\">"+ duration_string + "</span></p></body></html>"), None))


	def update_label_signal(self, qtime_obj):
		total_seconds = (qtime_obj.minute() * 60) + qtime_obj.second()
		self.update_label(total_seconds)


	def pause_countdown(self):
		try:
			self.countdown_thread.terminate()
		except:
			pass
		self.startBtn.setText('Start')
		self.started = False
		self.paused = True


	def reset_countdown(self):
		if self.started is False and self.paused is False:
			pass  # if timer is not running nor paused, do nothing
		else:
			try:
				self.countdown_thread.terminate()
			except:
				pass
			self.startBtn.setText('Start')
			self.started = False
			self.update_label(self.inputTimeSec)


	def timer_finished(self):
		pygame.mixer.music.load('Caraway.mp3')
		pygame.mixer.music.play()

		QtGui.QMessageBox.information(self, 'Timer', 'Timer Finished!', QtGui.QMessageBox.Ok)
				
		self.reset_countdown()


	def enter_task(self):
		self.addTaskWindow = AddTaskPopup()
		self.connect(self.addTaskWindow, QtCore.SIGNAL('add_task(QString, QDateTime, QString)'), self.add_task)
		self.addTaskWindow.setFixedSize(300, 220)
		self.addTaskWindow.show()


	def add_task(self, description, deadline, priority):
		# hiding input windows
		try:  # when loading task data this will fail
			self.addTaskWindow.hide()
		except:
			pass

		try:  # when loading task data this will fail
			self.editTaskWindow.hide()
		except:
			pass

		self.now = QtCore.QDateTime.currentDateTime()  # updates current date time var
		msec_to_date = deadline.toMSecsSinceEpoch() - self.now.toMSecsSinceEpoch()
		sec, msec = divmod(msec_to_date, 1000)  # returns sec & milisec
		task_deadline_thread = countdownThread(sec)  # starts countdown to task

		deadlineMin = str(deadline.time().minute()) if deadline.time().minute() >= 10 else ("0"+str(deadline.time().minute()))
		task = "'" + description + "' until " + str(deadline.time().hour()) + ":" + deadlineMin + " on " + str(deadline.date().day()) + "/" + str(deadline.date().month()) + "/" + str(deadline.date().year()) + ' - ' + priority
		self.task_dict[deadline] = task  # add task to task list
		taskWidget = QtGui.QCheckBox(task)
		taskWidget.stateChanged.connect(lambda x: self.complete_task(taskWidget, deadline, task_deadline_thread))
		task_colour = self.get_task_colour(priority)  # get task colour based on priority
		taskWidget.setStyleSheet("QWidget { background-color: %s }" % task_colour)
		self.taskWidgetsVLayout.addWidget(taskWidget)

		self.connect(task_deadline_thread, QtCore.SIGNAL('timer_finished()'), self.task_due)
		task_deadline_thread.start()


	def get_task_colour(self, priority):
		if priority == 'Important and Urgent':
			task_colour = "#FF3015"
		elif priority == 'Important but not Urgent':
			task_colour = "#FF6A15"
		elif priority == 'Not Important but Urgent':
			task_colour = "#36FF15"
		else:  # 'Not Important and not Urgent'
			task_colour = "#15C9FF"
		return task_colour


	def task_due(self):
		pygame.mixer.music.load('Caraway.mp3')
		pygame.mixer.music.play()

		now = QtCore.QDateTime.currentDateTime()

		for key in self.task_dict.keys():
			# finds difference in seconds between current time and alarm
			# in order to find out which alarm is ringing and thus print the descr
			difference = abs(now.toTime_t() - key.toTime_t())
			if difference < 5:
				messageText = "Task '" + self.task_dict[key].split(' until ')[0] + "' is due now!" 
				QtGui.QMessageBox.information(self, 'Task Due', messageText, QtGui.QMessageBox.Ok)
				# self.task_dict.pop(key)  # maybe highlight ???????????????
				break


	def complete_task(self, task, deadline, deadline_thread):
		try:
			deadline_thread.terminate()
		except:
			pass

		# find the key of the corresponding task
		task_key = self.task_dict.keys()[self.task_dict.values().index(task.text())]
		self.task_dict.pop(task_key)  # remove from current tasks
		self.completed_tasks[deadline] = task.text()  # adds it to the completed task dict
		task.setParent(None)  # removes task from widget
		# print self.completed_tasks


	def show_task_history(self):
		self.historyWindow = TaskHistoryPopup(self.completed_tasks)
		# when a signal to recover task is received go to "recover_task" function
		self.connect(self.historyWindow, QtCore.SIGNAL('recover_task(QString, QDateTime)'), self.recover_task)
		self.historyWindow.show()


	def recover_task(self, task, deadline):
		now = QtCore.QDateTime.currentDateTime()  # updates current date time var
		task_priority = task.split(" - ")[1]
		if deadline < now:
			task_text = str(task.split(' until ')[0]).translate(None, "'")
			self.editTaskWindow = AddTaskPopup(task_text, task_priority)
			self.connect(self.editTaskWindow, QtCore.SIGNAL('add_task(QString, QDateTime, QString)'), self.add_task)
			self.editTaskWindow.setFixedSize(300, 220)
			self.editTaskWindow.show()
		else:
			msec_to_date = deadline.toMSecsSinceEpoch() - now.toMSecsSinceEpoch()
			sec, msec = divmod(msec_to_date, 1000)  # returns sec & milisec
			task_deadline_thread = countdownThread(sec)  # starts countdown to task
			self.task_dict[deadline] = task # add task to current task list
			taskWidget = QtGui.QCheckBox(task)
			taskWidget.stateChanged.connect(lambda x: self.complete_task(taskWidget, deadline, task_deadline_thread))
			task_colour = self.get_task_colour(task_priority)
			taskWidget.setStyleSheet("QWidget { background-color: %s }" % task_colour)
			self.taskWidgetsVLayout.addWidget(taskWidget)
			self.connect(task_deadline_thread, QtCore.SIGNAL('timer_finished()'), self.task_due)
			task_deadline_thread.start()


	def start_stopwatch(self):
		if self.stopwatch_running is False:
			self.stopwatch_running = True
			self.startBtn_2.setText('Stop')
			self.stopwatch_thread = stopwatchThread(self.stopwatch_running, self.milli_sec)
			self.connect(self.stopwatch_thread, QtCore.SIGNAL('update_stopwatch(int)'), self.update_stopwatch)
			self.stopwatch_thread.start()
		else:
			self.stopwatch_running = False
			self.startBtn_2.setText('Start')
			self.stopwatch_thread.terminate()


	def stop_stopwatch(self):
		if self.stopwatch_running is True:
			self.stopwatch_running = False
			self.startBtn_2.setText('Start')
			self.stopwatch_thread.terminate()

		self.milli_sec = 0
		self.update_stopwatch(self.milli_sec)
		self.lap_number = 1
		self.lap_list = []
		# you need to loop backwards. Because removing things from 
		# the beginning will shift items and change the order of items.
		for lap in reversed(range(self.lapTimeVLayout.count())):
			item = self.lapTimeVLayout.itemAt(lap)
			if isinstance(item, QtGui.QWidgetItem):
				item.widget().close()


	def take_lap_time(self):
		if self.stopwatch_running is True:
			if self.lap_list: # True if the list is not empty
				# finds current lap time in mSec and then converts to seconds
				current_lap_msec = self.milli_sec - self.lap_list[-1]
				sec, msec = divmod(current_lap_msec, 1000)  # returns sec & milisec
				# returns sec & milisec of the total accumulated time
				tot_sec, tot_msec = divmod(self.milli_sec, 1000)
			else:  # this is the first lap
				# directly convert to seconds
				sec, msec = divmod(self.milli_sec, 1000)  # returns sec & milisec
				# returns sec & milisec of the total accumulated time
				tot_sec = sec
				tot_msec = msec

			self.lap_list.append(self.milli_sec)  # adds total time to list
			duration_string = time.strftime("%M:%S", time.gmtime(sec))  # formats time to MM:SS
			milisec = '00' if msec == 0 else str(msec/10)
			# computes total accumulated time in MM:SS:MS format
			tot_duration_string = time.strftime("%M:%S", time.gmtime(tot_sec))
			tot_milisec = '00' if tot_msec == 0 else str(tot_msec/10)
			# formating final lap string
			lap_str = str(self.lap_number) + ". " + duration_string + ":" + milisec + ' ('+ tot_duration_string + ':' + tot_milisec + ')'
			self.lap_number += 1
			lapTime = QtGui.QLabel(_translate("MainWindow", ("<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:500;\">"+ lap_str + "</span></p></body></html>"), None))
			self.lapTimeVLayout.addWidget(lapTime)


	def update_stopwatch(self, milli_sec):
		self.milli_sec = milli_sec  # updating milli_sec value
		sec, msec = divmod(milli_sec, 1000)  # returns sec & milisec
		duration_string = time.strftime("%M:%S", time.gmtime(sec))  # formats time to MM:SS
		milisec = '00' if msec == 0 else str(msec/10)
		time_str = duration_string + ":" + milisec
		self.timeLabel_2.setText(_translate("MainWindow", ("<html><head/><body><p align=\"center\"><span style=\" font-size:48pt; font-weight:600;\">"+ time_str + "</span></p></body></html>"), None))


	def start_countdown_to_date(self):
		if self.countdown_to_date is False:
			if self.dateTimeEdit.dateTime() > self.now:  # if date in the future
				self.countdown_to_date = True
				self.countdownStart.setText('Clear')
				# find msec to the desired date and compute remaining seconds to date
				self.now = QtCore.QDateTime.currentDateTime()  # updates current date time var
				msec_to_date = self.dateTimeEdit.dateTime().toMSecsSinceEpoch() - self.now.toMSecsSinceEpoch()
				sec, msec = divmod(msec_to_date, 1000)  # returns sec & milisec
				self.update_countdown_to_date_label(sec)  # updates countdown label
				self.countdown_to_date_thread = countdownThread(sec)
				self.connect(self.countdown_to_date_thread, QtCore.SIGNAL('update_label(int)'), self.update_countdown_to_date_label)
				self.connect(self.countdown_to_date_thread, QtCore.SIGNAL('timer_finished()'), self.countdown_to_date_finished)
				self.countdown_to_date_thread.start()
			else:
				QtGui.QMessageBox.warning(self, 'Error', 'Countdown to the past is not supported!', QtGui.QMessageBox.Ok)
		else:
			self.countdown_to_date = False
			self.countdownStart.setText('Start')
			self.countdown_to_date_thread.terminate()
			self.update_countdown_to_date_label(0)
			self.update_date_time_widget()  # resets the dateTime widget to the current date time


	def update_countdown_to_date_label(self, seconds):
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		self.label.setText(_translate("MainWindow", ("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt; font-weight:600;\">" + str(days) + " days " + str(hours) + " hours</span></p><p align=\"center\"><span style=\" font-size:28pt; font-weight:600;\">" + str(minutes) + " minutes</span></p><p align=\"center\"><span style=\" font-size:28pt; font-weight:600;\">" + str(seconds) +" seconds</span></p></body></html>"), None))


	def countdown_to_date_finished(self):
		pygame.mixer.music.load('Caraway.mp3')
		pygame.mixer.music.play()
		self.countdownStart.setText('Start')
		self.countdown_to_date = False

		QtGui.QMessageBox.information(self, 'Countdown', 'Countdown to date finished!', QtGui.QMessageBox.Ok)


	def update_date_time_widget(self):
		if self.tabWidget.currentIndex() == 4:  # if countdown to date is opened	
			if self.countdown_to_date is False:  # and we are not curently counting down
				self.now = QtCore.QDateTime.currentDateTime()  # gets current date time
				self.dateTimeEdit.setDateTime(self.now)  # sets the dateTimeEdit to now


	def set_alarm(self):
		# opens window that lets you add an alarm
		self.addAlarmWindow = AddAlarmPopup()
		self.connect(self.addAlarmWindow, QtCore.SIGNAL('add_alarm(QString, QDateTime)'), self.create_alarm)
		self.addAlarmWindow.setFixedSize(300, 140)
		self.addAlarmWindow.show()


	def create_alarm(self, alarmDescription, alarmDateTime):
		try:  # when loading alarm data this will fail
			self.addAlarmWindow.hide()
		except:
			pass

		self.now = QtCore.QDateTime.currentDateTime()  # updates current date time var
		msec_to_date = alarmDateTime.toMSecsSinceEpoch() - self.now.toMSecsSinceEpoch()
		sec, msec = divmod(msec_to_date, 1000)  # returns sec & milisec
		# adds the alarm time and descriptions in a dictionary
		# so that when the alarm rings it can display its descr
		self.alarm_dict[alarmDateTime] = alarmDescription

		# adds a 0 in front of the minutes if <10
		alarmMinute = str(alarmDateTime.time().minute()) if alarmDateTime.time().minute() >= 10 else ("0"+str(alarmDateTime.time().minute()))
		alarmBtnText = "'" + alarmDescription + "' for " + str(alarmDateTime.time().hour()) + ":" + alarmMinute + " on " + str(alarmDateTime.date().day()) + "/" + str(alarmDateTime.date().month()) + "/" + str(alarmDateTime.date().year())
		alarmBtn = QtGui.QPushButton(alarmBtnText)
		
		alarm_thread = countdownThread(sec)
		
		alarmBtn.clicked.connect(lambda x: self.alarm_clicked(alarmBtn, alarm_thread))

		self.alarmWidgetsVLayout.addWidget(alarmBtn)

		self.connect(alarm_thread, QtCore.SIGNAL('timer_finished()'), self.ring_alarm)
		alarm_thread.start()
		

	def alarm_clicked(self, alarmBtn, alarm_thread):
		# ask user if he wants to remove the selected alarm
		choice = QtGui.QMessageBox.question(self, 'Remove Alarm', 'Would you like to remove the selected alarm?',
			QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:
			alarmBtn.setParent(None)
			alarm_thread.terminate()
		else:
			pass


	def ring_alarm(self):
		pygame.mixer.music.load('Caraway.mp3')
		pygame.mixer.music.play()

		now = QtCore.QDateTime.currentDateTime()

		for key in self.alarm_dict.keys():
			# finds difference in seconds between current time and alarm
			# in order to find out which alarm is ringing and thus print the descr
			difference = abs(now.toTime_t() - key.toTime_t())
			if difference < 5:
				QtGui.QMessageBox.information(self, 'Alarm', self.alarm_dict[key], QtGui.QMessageBox.Ok)
				self.alarm_dict.pop(key)  # removes alarm entry from dict
				break


def main():
	app = QtGui.QApplication(sys.argv)
	timer_obj = TimerApp()
	timer_obj.show()
	app.exec_()

if __name__ == '__main__':
    main()
