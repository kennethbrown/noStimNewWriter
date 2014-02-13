#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# WRITER.PY
#   This module contains two functions for separately writing audio and tracking data. Tracking data is written to 
#	a file whose name is determined by TRACKING_OUTPUT and audio data output file names are determined by AUDIO_OUTPUT_AI0
#	and AUDIO_OUTPUT_AI1. If you change the names of the files, make sure to maintain the .csv file extension at the end. 
# USAGE:
#   This script is called from the command line using the function
#		python track.py protocol/stim 'invid2.mpg'
#	where protocol/track is protocol if you want to stimulate based on a set protocol (whose parameters can be modified in stimProtocol.py) or
#	track if you want to stimulate based on real-time tracking. 'inVid2.mpg' is an optional argument that can be replaced by the name of any video
#	file contained in the program directory. If included, this argument indicates that tracking will be based on a video-file stream rather than a 
#	live webcam stream
# NOTES:
#	Every time the 'start' button is pressed on the main tracking screen, these files get overwritten. In order to preserve data from 
#	experimental runs, make sure to change the file names in finder/windows explorer. Once data is overwritten, there is no way to 
#	recover it. 
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
################################################################################################################################################################################################################
#-IMPORTING DEPENDENCIES---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

import csv #	python csv pibrary for writing to csv files
from settings import *
import h5py
from decimal import *
#getcontext().prec = 9
import numpy as np

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
################################################################################################################################################################################################################
#-FILE NAMES AND DATA FIELDS---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

TRACKING_OUTPUT = 'tracking output.csv' # Name for data output file (must have .csv extension)
AUDIO_OUTPUT_ai0 = 'audio output ai0.csv' # Name for audio output file from channel ai0 (must have .csv extension)
AUDIO_OUTPUT_ai1 = 'audio output ai1.csv' # Name for audio output file from channel ai1 (must have .csv exntension)

# Field names for tracking output file
FIELDS = ['X Position', 'Y Position', 'Time', 'Angle', 'Speed', 'Active', 'Inactivity Time', 'Approaching Restrainer', 'Restrainer Approach Time',
           'Restrainer Ignore Time', 'Stimulate', 'Tracking Timestamp']

# Delimiter for the csv files. Set to ',' by default but can also be the tab character '\t'
DELIMITER = ','

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
################################################################################################################################################################################################################
#-WRITING TRACKING DATA TO FILE--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Data gets written to the file whose name is determined by the constant variable TRACKING_OUTPUT
def writeToFile(arenaPoint,timeStamp,angle,speed,active,inactiveElapsed,inRestrainer,approachElapsed,ignoreElapsed,stimulate, firstLine,trackT):
	# Code from the defs.py module determines if this is the first line being written to the data output file
	# If the data point being passed to this function occured within 1 second of pressing 'start recording' then
	# it is assumed to be the first line of the file. If a csv file with the name indicated by TRACKING_OUTPUT
	# already exists in the program directory, the first line case will overwrite the existing file. If no csv
	# file by the name exists in the directory, the code creates a new csv file. 
	if firstLine:
		doc = open(TRACKING_OUTPUT, 'wb')

	# If the tracking data point being passed is not determined to be the first line of the file, this function
	# opens up the currently existing csv file whose name is determined by TRACKING_OUTPUT and appends
	# the data point to the last row of the file.
	else:
		doc = open(TRACKING_OUTPUT, 'ab')
	writer = csv.DictWriter(doc, fieldnames = FIELDS, delimiter = DELIMITER)
	
	
	# Extract the x- and y-coordinates of the tracking point from the passed variable arenaPoint
	xPos = arenaPoint[0]
	yPos = arenaPoint[1]

	# If we are writing the first line of the csv file, write a header (column labels, determined by the
	# constant variable FIELDS) before writing the first data point. 
	if firstLine:
		writer.writeheader()

	# Write the passed data point to the csv file using python's dictionary structure
	writer.writerow({'X Position': xPos, 'Y Position': yPos, 'Time': timeStamp, 'Angle': angle, 'Speed': speed, 'Active': active, 'Inactivity Time': inactiveElapsed, 
		'Approaching Restrainer': inRestrainer, 'Restrainer Approach Time': approachElapsed,
           'Restrainer Ignore Time':ignoreElapsed, 'Stimulate': stimulate, 'Tracking Timestamp': trackT})
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
################################################################################################################################################################################################################
#-WRITING TRACKING DATA TO FILE--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# This function writes audio data to the csv files whose names are determined by the constant variables
# AUDIO_OUTPUT_ai0 and AUDIO_OUTPUT_ai1. This function only gets called if the number of mics being 
# used is 1 or 2. 
def writeAudio(recording, NUM_MICS):
	# For the case that 1 mic is being used. The file whose name is determined
	# by AUDIO_OUTPUT_ai1 does not get modified in this case
	if NUM_MICS == 1:
		# open the AUDIO_OUTPUT_ai0 docoument. Note that any currently
		# existing csv file with the same name in the program directory 
		# gets overwritten
		doc = open(AUDIO_OUTPUT_ai0, 'wb')

		# Initialize a csv writer object for writing data to the csv file
		writer = csv.writer(doc)
		
		f = h5py.File('audioOut.hdf5', 'w')
		grp = f.create_group("trial")

		# Parse each data point (row) contained in the timeStamps list.
		# Each row consists of a tuple (one-dimensional array) whose first 
		# element is the audio reading and whose second element is the 
		# audio timestamp. 
		#print recording.timeStamps
		timestamps = map(lambda x: x[1], recording.timeStamps)
		step = 1.0 / SAMPLE_RATE
		# print timestamps
		# print BUFFER_SIZE
		# print step
		timestamps = map(lambda x: [x] + [x+i*step for i in range(1,BUFFER_SIZE)], timestamps)
		timestamps = [ts for lst in timestamps for ts in lst]
		f.create_dataset("voltage", data=np.array(recording.a)) #compression="gzip")
		f.create_dataset("time", data=np.array(timestamps)) #compression="gzip")
		data = zip(recording.a, timestamps)
		for row in data:
			#extract the audio reading
			left = row[0]
			#extract the timestamp
			right = row[1]
			#write the data point to the 
			#csv file
			writer.writerow([left,right])
	# For the case that 2 mics are being used. Both files whose names are
	# determined by AUDIO_OUTPUT_ai0 and AUDIO_OUTPUT_ai1 get overwritten
  # TODO as yet unadjusted to write all data
	elif NUM_MICS == 2:
		# Open the two audio csv files. Any existing files with the same names
		# contained in the program directory get overwritten
		doc1 = open(AUDIO_OUTPUT_ai0, 'wb')
		doc2 = open(AUDIO_OUTPUT_ai1, 'wb')

		# Initialize two seperate csv writer objects for writing 
		# to the two csv files. 
		writer1 = csv.writer(doc1)
		writer2 = csv.writer(doc2)

		# In this case, timeStamps consists of two lists each having
		# the same format as the timeStamps structure in the NUM_MICS = 1
		# case above. Each list is referenced by its channel name using the
		# python dictionary structure. The timestamp for the data point
		# at any given index of the 'ai0' and 'ai1' list is the same
		# since they were taken at the same time (e.g. 
		# timeStamps['ai0'][index][1] = timeStamps['ai1'][index][1]
		# for all values of 'index')

		# First, we parse every data point contained in the 'ai0' list
		# of data points.
		for row in timeStamps['ai0']:
			# Extact the 'ai0' audio reading
			left = row[0]
			# Extract the timestamp
			right = row[1]
			# Write the data point to the AUDIO_OUTPUT_ai0 file
			writer1.writerow([left,right])

		# Now we parse every data point contained in the 'ai1' list
		# of data points
		for row in timeStamps['ai1']:
			# Extract the 'ai1' audio reading
			left = row[0]
			# Extract the timestamp
			right = row[1]
			# Write the data point to the AUDIO_OUTPUT_ai1 file
			writer2.writerow([left, right])
