### DEFINES THE FUNCTION USED FOR SYNCING AUDIO AND TRACKING DATA TOGETHER INTO ONE DATA OUTPUT FILE ###


import csv
from writer import *

DATA_OUT = "Data Output.csv"
FIELDS = ['X Position', 'Y Position', 'Time Elapsed', 'Angle', 'Speed', 'Active', 'Inactivity Time', 'Approaching Restrainer', 
		'Restrainer Approach Time', 'Restrainer Ignore Time', 'Stimulate', 'Audio Signal Ai0',
		'Audio Signal Ai1',  'Audio Timestamp', 'Tracking Timestamp']
DELIMITER = ','


def sync(audioData, NUM_MICS):
	tracking = open(TRACKING_OUTPUT, 'rb')
	# audio = open(AUDIO_OUTPUT, 'rb')
	out = open(DATA_OUT, 'wb')
	trackReader = csv.reader(tracking)
	# audioReader = csv.reader(audio)
	writer = csv.DictWriter(out, fieldnames = FIELDS, delimiter = DELIMITER)
	writer.writeheader()
	trackData = []
	# audioData = []

	trackReader.next()
	lastIndex = -1
	lastIndexai0 = -1
	lastIndexai1 = -1

	for trackRow in trackReader:
		# trackData.append(row)
		# print row
		trackTime = trackRow[11]
		minDiff = 100
		count = 0
		index = 0
		indexai0 = 0
		indexai1 = 0
		

		if NUM_MICS == 0:
			row = {'X Position':trackRow[0], 'Y Position':trackRow[1], 'Time Elapsed':trackRow[2],
				'Angle':trackRow[3], 'Speed':trackRow[4], 'Active':trackRow[5], 
				'Inactivity Time':trackRow[6], 'Approaching Restrainer':trackRow[7], 
				'Restrainer Approach Time':trackRow[8],
				'Restrainer Ignore Time':trackRow[9], 'Stimulate':trackRow[10], 
				'Audio Signal Ai0': 'NA', 'Audio Timestamp':'NA', 
				'Tracking Timestamp':trackRow[11], 'Audio Signal Ai1': 'NA'}
			writer.writerow(row)

		elif NUM_MICS == 1:

			while count < len(audioData):
				audioRow = audioData[count]
				audioTime = audioRow[1]
				# print (audioTime, trackTime)
				tempDiff = abs(float(trackTime) - float(audioTime))
				if tempDiff < minDiff:
					minDiff = tempDiff
					index = count
				count += 1

			audioRow = audioData[index]

			row = {'X Position':trackRow[0], 'Y Position':trackRow[1], 'Time Elapsed':trackRow[2],
				'Angle':trackRow[3], 'Speed':trackRow[4], 'Active':trackRow[5], 
				'Inactivity Time':trackRow[6], 'Approaching Restrainer':trackRow[7], 
				'Restrainer Approach Time':trackRow[8],
				'Restrainer Ignore Time':trackRow[9], 'Stimulate':trackRow[10], 
				'Audio Signal Ai0': audioRow[0], 'Audio Timestamp': audioRow[1], 
				'Tracking Timestamp':trackRow[11], 'Audio Signal Ai1': 'NA'}

			if lastIndex != index:
				writer.writerow(row)
			lastIndex = index

		elif NUM_MICS == 2:

			while count < len(audioData['ai0']):
				audioRow = (audioData['ai0'][count][0],audioData['ai1'][count][0],audioData['ai0'][count][1])
				audioTime = audioRow[2]
				# print (audioTime, trackTime)
				tempDiff = abs(float(trackTime) - float(audioTime))
				if tempDiff < minDiff:
					minDiff = tempDiff
					index = count
				count += 1

			audioRow = (audioData['ai0'][index][0],audioData['ai1'][index][0],audioData['ai0'][index][1])

			row = {'X Position':trackRow[0], 'Y Position':trackRow[1], 'Time Elapsed':trackRow[2],
				'Angle':trackRow[3], 'Speed':trackRow[4], 'Active':trackRow[5], 
				'Inactivity Time':trackRow[6], 'Approaching Restrainer':trackRow[7], 
				'Restrainer Approach Time':trackRow[8],
				'Restrainer Ignore Time':trackRow[9], 'Stimulate':trackRow[10], 
				'Audio Signal Ai0': audioRow[0], 'Audio Timestamp': audioRow[2], 
				'Tracking Timestamp':trackRow[11], 'Audio Signal Ai1': audioRow[1]}

			if lastIndex != index:
				writer.writerow(row)
			lastIndex = index



		# elif NUM_MICS == 2:
		# 	audioDataai0 = audioData['ai0']
		# 	audioDataai1 = audioData['ai1']
		# 	while count < len(audioDataai0):
		# 		audioRow = audioDataai0[count]
		# 		audioTime = audioRow[1]
		# 		tempDiff = abs(float(trackTime) - float(audioTime))
		# 		if tempDiff < minDiff:
		# 			minDiff = tempDiff
		# 			indexai0 = count
		# 		count += 1

		# 	minDiff = 100
		# 	count = 0
		# 	index = 0
		# 	indexai0 = 0
		# 	indexai1 = 0


		# 	while count < len(audioDataai1):
		# 		audioRow = audioDataai1[count]
		# 		audioTime = audioRow[1]
		# 		tempDiff = abs(float(trackTime) - float(audioTime))
		# 		if tempDiff < minDiff:
		# 			minDiff = tempDiff
		# 			indexai1 = count
		# 		count += 1

		# 	audioRowai0 = audioDataai0[indexai0]
		# 	audioRowai1 = audioDataai1[indexai1]

		# 	row = {'X Position':trackRow[0], 'Y Position':trackRow[1], 'Time Elapsed':trackRow[2],
		# 		'Angle':trackRow[3], 'Speed':trackRow[4], 'Active':trackRow[5], 
		# 		'Inactivity Time':trackRow[6], 'Approaching Restrainer':trackRow[7], 
		# 		'Restrainer Approach Time':trackRow[8],
		# 		'Restrainer Ignore Time':trackRow[9], 'Stimulate':trackRow[10], 
		# 		'Audio Signal Ai0': audioRowai0[0], 'Audio Timestamp Ai0':audioRowai0[1], 
		# 		'Tracking Timestamp':trackRow[11], 'Audio Signal Ai1': audioRowai1[0], 'Audio Timestamp Ai1':audioRowai1[1] }

		# 	if lastIndexai0 != indexai0 and lastIndexai1 != indexai1:
		# 		writer.writerow(row)
		# 	lastIndexai0 = indexai0
		# 	lastIndexai1 = indexai1


		else: 
			print "ERROR: Number of Mics must be 0, 1, or 2"
			quit()

	# for audioRow in audioReader:
	# 	audioTime = audioRow[1]
	# 	minDiff = 100
	# 	count = 0
	# 	index = 0
	# 	while count < len(trackData):
	# 		trackRow = trackData[count]
	# 		trackTime = trackRow[11] 
	# 		tempDiff = abs(float(trackTime) - float(audioTime))
	# 		if tempDiff < minDiff:
	# 			minDiff = tempDiff 
	# 			index = count
	# 		count +=1
	# 	trackRow = trackData[index]
	# 	row = {'X Position':trackRow[0], 'Y Position':trackRow[1], 'Time Elapsed':trackRow[2],
	# 	      'Angle':trackRow[3], 'Speed':trackRow[4], 'Active':trackRow[5], 
	# 	      'Inactivity Time':trackRow[6], 'Approaching Restrainer':trackRow[7], 
	# 	      'Restrainer Approach Time':trackRow[8],
	#           'Restrainer Ignore Time':trackRow[9], 'Stimulate':trackRow[10], 
	#           'Audio Frequency':audioRow[0], 'Audio Timestamp':audioRow[1], 
	#           'Tracking Timestamp':trackRow[11]}
	# 	writer.writerow(row)



# for row in audioReader:
# 	audioData.append(row)

# for row in 