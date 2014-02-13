#--------------------------------------------------------------------------------------------------------------------------------------------#
# AUDIO.PY
#   This script defines python functions for interfacing with a DAQ board to record audio signals. The Record class defines a task for collecting
#   data from one microphone (plugged into channel ai0). The MultiRecord class defines a task for collecting data from two microphones (plugged 
#   into ai0 and ai1). Script currently does not appear to be sampling at a high enough rate. This script uses the PyDAQmx library which is a python
#   extension of National Instrument's NiDAQmx driver (native C functions).
# USAGE:
#   import the functions from this script using the line 
#            from audio import *
#   at the top of your script. Create a Record or MultiRecord class to open the DAQ board channels and begin collecting data. Note that for
#   a Record object, calling Record.StartTask() begins data collection whereas for a MultiRecord Object, calling MultiRecord.readAll() returns
#   the current reading from the two channels.
#--------------------------------------------------------------------------------------------------------------------------------------------#


#-IMPORTING DEPENDENCIES---------------------------------------------------------------------------------------------------------------------#

from writer import *
from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
from numpy import zeros
import numpy
import time

from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *

#--------------------------------------------------------------------------------------------------------------------------------------------#


#-RECORD CLASS FOR SINGLE MICROPHONE INPUT---------------------------------------------------------------------------------------------------#
class Record(Task):
    # Constructor for a Record object
	#krb: __init__ is called automatically when the Record object is instantiated, and the object is passed as the first argument (self by convention)
	#krb: creates self.data, an array of 1000 zeros, and self.a, an empty list, and self.timeStamps, another empy list
	#krb: creates voltage channel and configures it
    def __init__(self):
        Task.__init__(self)

        # Data stores the readings from the input channel
        self.data = zeros(1000)

        # An auxiliary structure for use with Data variable
        self.a = []

        # Similar to Data, except every element contains a reading and a timestamp from the system clock
        self.timeStamps = []

        # Create and configure channel ai0
		#krb: CreateAIVoltageChan creates a voltage channel and adds it to the task specified (in C, by the first argument, in PyDAQ I think the self. prefix provides the target task)
		#krb: DAQmx_Val_RSE parameter is for the input terminal config, and sets it to referenced single end mode
		#krb: DAQmx_Val_Volts sets the voltage unit as volts
		#krb: need to figure out appropriate voltage range in CreateAIVoltageChan (Gabe was using -10 to 10) perhaps the conditioning amplifier keeps signal in certain range
		#krb: On our setup the physical channel will always be ai0, but the device channel won't always be dev2
        self.CreateAIVoltageChan("Dev1/ai0","",DAQmx_Val_RSE,-1.0,1.0,DAQmx_Val_Volts,None)
		#krb: CfgSampClkTiming gives the source and rate of the sample clock and passses how many samples to aquire (either in absolute terms or in terms of buffer size per transfer)
        #krb: sample rate in CfgSampClkTiming should theoretically be 2x max tone of interest (i.e. >200khz or >200000 samples/second)
		#krb: first argument of CfgSampClkTiming is the source terminal of the sample clock, and should be NULL or OnboardClock to use the DAQ's internal clock
        self.CfgSampClkTiming("",100000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,1000)
		#krb: these two autoregister functions are callbacks, referenced in nidaqmx help\C functions\task configuration+control\events
		#krb: the first argument is the trigger, which here is a specified number of samples into the buffer. 
		#krb: The last argument (of both register fxns) is the triggered event. The zero values mean that the callback fxn is unregistered i.e. nothing happens
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,1000,0)
        self.AutoRegisterDoneEvent(0)
	
	#krb: fxn to give the frequency domain signal calculated from the data array
	# def fft(self)
		# freqs = numpy.rfft(self.data)/len(self.data)
		# return freqs
		

    # Configure the automatic recording of input signals from channel ai0
    def EveryNCallback(self):
        read = int32()
		#krb: ReadAnalogF64 takes floating point samples from a task and puts them in an array (in this case, self.data)
		#krb: arg1 - number of samples to take, arg2 - timeout in s - 0 means one try, -1 means infinite wait, if timeout elapses fxn passes an error
		#krb: arg3 - interleaved or non interleaved, arg4 - array to put data into, arg5 - size of the array, arg6 - how many samples have been read from each channel (?), arg7 - reserved for future developments - should be null
        self.ReadAnalogF64(1000,10.0,DAQmx_Val_GroupByScanNumber,self.data,1000,byref(read),None)
		#adds all of the self.data array to the end of aucillary data structure a
        self.a.extend(self.data.tolist())
		#adds the first entry in self.data to the timestamped list - is such a small subset of the voltage data useful (assuming this gives 1/1000th of the voltage reads)
        self.timeStamps.append((self.data[0],time.clock()))
        
    # Configure return value when the Record object stops recording
    def DoneCallback(self, status):
        print "Status",status.value
        return 0 # The function should return an integer

#--------------------------------------------------------------------------------------------------------------------------------------------#

print 'initiated'
recording = Record()
recording.StartTask()
for x in range(0,10):
	bottom = x*100
	top = x*100+10
	print recording.a[bottom:top]
	time.sleep(1)
recording.StopTask()
print recording.a[0:100]
print recording.a[10000:10100]
recording.ClearTask()


# raw_input('Press Enter to Interrupt\n')
# print 'heres data\n'
# print recording.data
# print 'heres a\n'
# print recording.a
# print 'heres timeStamps\n'
# print recording.timeStamps