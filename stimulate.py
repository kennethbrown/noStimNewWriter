### CONTAINS THE FUNCTIONS FOR INTERACTING WITH THE MASTER-8 STIMULATOR ###




from Master8 import *
global waitTime
import time


DURATION = 500 #duration, in milliseconds, of each pulse
# DELAY = 1 #duration, in illiseconds, 
INTERVAL = 1000 #duration, in milliseconds, of the time interval between the beginning of consecutive pulses (includes the length of the pulse)
TIME = 5 #duration, in seconds for which trains of pulses should be applied 
NUM_PULSES = 5 #number of pulses per train
TRIGGER_WAIT = 2 #duration, in seconds, of the pause between trains of pulses (includes train time)

waitTime = TIME


def stimulateOn(lastStimulate, stimulator, prevStimStart): #, prevStimTime):
	# stimulator.setChannelVoltage(1, 2)

	# global stimulator
	if (lastStimulate == False):
		# stimulator.changeChannelDuration(1,time)
		# stimulator.changeChannelMode(1,TRAIN)
		stimStart = time.clock()
		stimTime = 0
		offTime = 0
		stimEnd = time.clock()
	else:
		stimStart = prevStimStart
		stimTime = round(time.clock() - stimStart, 0)
		offTime = 0
		stimEnd = time.clock()

	return (stimStart, stimTime, stimEnd, offTime)

def stimulateOff(lastStimulate, stimulator, prevStimEnd):
	# global stimulator
	if (lastStimulate):
		# stimulator.changeChannelMode(1,OFF)
		stimEnd = time.clock()
		offTime = 0
		stimTime = 0
		stimStart = time.clock()

	else:
		stimEnd = prevStimEnd
		offTime = round(time.clock() - stimEnd, 0)
		stimTime = 0
		stimStart = time.clock()

	return (stimStart, stimTime, stimEnd, offTime)