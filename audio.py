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

from settings import *

import numpy
import time
from h5py import *
import h5py
from PyDAQmx import *
from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxCallBack import *
from threading import *
import copy
import csv

#--------------------------------------------------------------------------------------------------------------------------------------------#

#-RECORD CLASS FOR SINGLE MICROPHONE INPUT---------------------------------------------------------------------------------------------------#
class Record(Task):
    # Constructor for a Record object
    def __init__(self):
	
        Task.__init__(self)

        # Data stores the readings from the input channel
        self.data = numpy.zeros(BUFFER_SIZE)
        self.a = []
        self.threads = []
		#self.timeList = TIMESTEP*(arange(0,WRITE_SIZE))
        self.timeStampTemplate = numpy.arange(0,WRITE_SIZE*TIMESTEP,TIMESTEP)
        # HDF5 datasets to which we will stream the incoming data
        # sampleCounter is used for indexing into these datasets
        #self.hdf5Out = h5py.File('audio_output.hdf5', 'w')
        # self.voltageOutput = self.hdf5Out.create_dataset('voltage', (NUMBER_OF_AUDIO_SAMPLES,))
        # self.timeStampOutput = self.hdf5Out.create_dataset('time', (NUMBER_OF_AUDIO_SAMPLES,))
        self.sampleCounter = 0
        # Create and configure channel ai0
        self.CreateAIVoltageChan("Dev2/ai0","",DAQmx_Val_RSE,-10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming("",SAMPLE_RATE,DAQmx_Val_Rising,DAQmx_Val_ContSamps,BUFFER_SIZE)
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,BUFFER_SIZE,0)
        #self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,WRITE_SIZE,0,self.writeCallback)
        self.AutoRegisterDoneEvent(0)
        
    def write(self, ary, counterValue, timestamp):
        print "start writing"
        hdf5Out = h5py.File('audio_output' + str(timestamp) + '.hdf5', 'w')
        voltageOutput = hdf5Out.create_dataset('voltage', (NUMBER_OF_AUDIO_SAMPLES,))
        timeStampOutput = hdf5Out.create_dataset('time', (NUMBER_OF_AUDIO_SAMPLES,))
        timeStamps = self.timeStampTemplate + timestamp
        irange = range(counterValue,counterValue + WRITE_SIZE)
        voltageOutput[irange] = numpy.zeros(NUMBER_OF_AUDIO_SAMPLES)
        timeStampOutput[irange] = numpy.zeros(NUMBER_OF_AUDIO_SAMPLES)
        hdf5Out.close()
        print "write successful"
        
    def writeCSV(self, ary, counterValue, timestamp):
        print "starts writing csv"
        timeStamps = self.timeStampTemplate + timestamp
        irange = range(counterValue, counterValue + WRITE_SIZE)
        doc = open('audioCSV' + str(timestamp) + '.csv', 'wb')
        writer = csv.writer(doc)
        for i in range(len(ary)):
			left = ary[i]
			right = timeStamps[i]
			writer.writerow([left,right])
        print "write successful"
		
    # Configure the automatic recording of input signals from channel ai0
    def EveryNCallback(self):
        read = int32()
        self.ReadAnalogF64(BUFFER_SIZE,10.0,DAQmx_Val_GroupByScanNumber,self.data,BUFFER_SIZE,byref(read),None)
        self.a.extend(self.data.tolist())
        self.sampleCounter += 1000
        if self.sampleCounter % (WRITE_SIZE) == 0:
            thr = Thread(target=self.writeCSV, args=(copy.copy(self.a), self.sampleCounter, time.clock()))
            thr.start()
            self.threads.append(thr)
            self.a = []
			# print "called"
			# ary = list(self.a)
			# timenow = time.clock()
			# timeStamps = self.timeStampTemplate + timenow
			#timestamps = timenow+i*TIMESTEP for i in range(WRITE_SIZE)]
			# irange = range(self.sampleCounter, self.sampleCounter+WRITE_SIZE)
			# self.voltageOutput[irange] = ary
			# self.timeStampOutput[irange] = timeStamps
			# self.a = []
        
	
        
	
    # Configure return value when the Record object stops recording
    def DoneCallback(self, status):
        self.hdf5Out.close()
        print "Status",status.value
        for thr in self.threads:
            thr.join()
        return 0 # The function should return an integer

#--------------------------------------------------------------------------------------------------------------------------------------------#


# TODO has not been adjusted to use the appropriate sample rate
#-MULTIRECORD CLASS FOR TWO MICROPHONES------------------------------------------------------------------------------------------------------#
class MultiRecord():

    # Constructor for a MultiRecord Object, reads the names passed to constructors and 
    # creates a task to record input from all specified channels
    def __init__(self,physicalChannel, limit = None, reset = False):
        if type(physicalChannel) == type(""):
            self.physicalChannel = [physicalChannel]
        else:
            self.physicalChannel  =physicalChannel
        self.numberOfChannel = physicalChannel.__len__()
        if limit is None:
            self.limit = dict([(name, (-10.0,10.0)) for name in self.physicalChannel])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in self.physicalChannel])
        else:
            self.limit = dict([(name, limit[i]) for  i,name in enumerate(self.physicalChannel)])           
        if reset:
            DAQmxResetDevice(physicalChannel[0].split('/')[0] )

    # Configuration of a MultiRecord Object
    def configure(self):

        # Create one task handle per Channel
        taskHandles = dict([(name,TaskHandle(0)) for name in self.physicalChannel])
        for name in self.physicalChannel:
            DAQmxCreateTask("",byref(taskHandles[name]))
            DAQmxCreateAIVoltageChan(taskHandles[name],name,"",DAQmx_Val_RSE,
                                     self.limit[name][0],self.limit[name][1],
                                     DAQmx_Val_Volts,None)
        self.taskHandles = taskHandles

    # Reads the signal from all the MultiRecord's channels and returns a dictionary of readings indexed by channel name
    def readAll(self):
        return dict([(name,self.read(name)) for name in self.physicalChannel])

    # Reads the signal from a single channel. For use in the readAll function. 
    def read(self,name = None):
        if name is None:
            name = self.physicalChannel[0]
        taskHandle = self.taskHandles[name]                    
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((1,), dtype=numpy.float64)
        read = int32()
        DAQmxReadAnalogF64(taskHandle,1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
        DAQmxStopTask(taskHandle)
        return (data[0],time.clock())

#--------------------------------------------------------------------------------------------------------------------------------------------#
