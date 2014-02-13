### Defines Functions for writing csv data output files ###

import csv

TRACKING_OUTPUT = 'tracking output.csv'
AUDIO_OUTPUT_ai0 = 'audio output ai0.csv'
AUDIO_OUTPUT_ai1 = 'audio output ai1.csv'
FIELDS = ['X Position', 'Y Position', 'Time', 'Angle', 'Speed', 'Active', 'Inactivity Time', 'Approaching Restrainer', 'Restrainer Approach Time',
           'Restrainer Ignore Time', 'Stimulate', 'Tracking Timestamp']
DELIMITER = ','

def writeToFile(arenaPoint,timeStamp,angle,speed,active,inactiveElapsed,inRestrainer,approachElapsed,ignoreElapsed,stimulate, firstLine,trackT):
	if firstLine:
		doc = open(TRACKING_OUTPUT, 'wb')
	else:
		doc = open(TRACKING_OUTPUT, 'ab')
	writer = csv.DictWriter(doc, fieldnames = FIELDS, delimiter = DELIMITER)
	
	
	xPos = arenaPoint[0]
	yPos = arenaPoint[1]
	if firstLine:
		writer.writeheader()
	writer.writerow({'X Position': xPos, 'Y Position': yPos, 'Time': timeStamp, 'Angle': angle, 'Speed': speed, 'Active': active, 'Inactivity Time': inactiveElapsed, 
		'Approaching Restrainer': inRestrainer, 'Restrainer Approach Time': approachElapsed,
           'Restrainer Ignore Time':ignoreElapsed, 'Stimulate': stimulate, 'Tracking Timestamp': trackT})





def writeAudio(timeStamps, NUM_MICS):
	if NUM_MICS == 1:
		doc = open(AUDIO_OUTPUT_ai0, 'wb')
		writer = csv.writer(doc)
		for row in timeStamps:
			left = row[0]
			right = row[1]
			writer.writerow([left,right])
	elif NUM_MICS == 2:
		doc1 = open(AUDIO_OUTPUT_ai0, 'wb')
		doc2 = open(AUDIO_OUTPUT_ai1, 'wb')
		writer1 = csv.writer(doc1)
		writer2 = csv.writer(doc2)
		for row in timeStamps['ai0']:
			left = row[0]
			right = row[1]
			writer1.writerow([left,right])
		for row in timeStamps['ai1']:
			left = row[0]
			right = row[1]
			writer2.writerow([left, right])




# writeToFile(arenaPoint =(0,0),timeStamp =0,angle =0,speed =0,active =False,inactiveElapsed=0,inRestrainer=False,approachElapsed=0,
# 	ignoreElapsed=0,stimulate=False, firstLine=True)

# writeToFile(arenaPoint =(3,4),timeStamp =1,angle =0,speed =5,active =True,inactiveElapsed=0,inRestrainer=False,approachElapsed=0,
# 	ignoreElapsed=1,stimulate=True, firstLine=False)
