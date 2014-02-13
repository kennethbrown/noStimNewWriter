from Master8 import *
import time


DURATION = 500 #milliseconds
DELAY = 1 #milliseconds
INTERVAL = 1000 #time interval, in milliseconds, between the beginning of consecutive pulses
TIME = 500 #duration, in milliseconds for which trains of pulses should be applied 
NUM_PULSES = 5 #number of pulses per train
TRIGGER_WAIT = 2 #duration, in seconds, of the pause between trains of pulses

stimulator = Master8()
# print stim.c

# while True:
duration = DURATION * (.001)
delay = DELAY *(.001)
interval = INTERVAL * (.001)
Time = TIME * (.001)

stimulator.setChannelDuration(1,duration)
stimulator.setChannelDelay(1,delay)
stimulator.setChannelInterval(1,interval)
stimulator.setChannelM(1,NUM_PULSES)
# stimulator.setChannelVoltage(1, 2)
stimulator.changeChannelMode(1,TRAIN)

while(True):
	time.sleep(TRIGGER_WAIT)
	stimulator.trigger(1)

# setChannelVoltage(self, channel, voltage):

# stimulator.changeChannelMode(1,OFF)

# print stim.connected
# while True:
# stim.changeChannelMode(1,FREE_RUN)
# print stim.cmlist




# print stim.c

# stim.changeChannelMode(1,FREE_RUN)

# time.sleep(5)

# stim.changeChannelMode(1,OFF)