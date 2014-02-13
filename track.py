### THE MAIN SCRIPT FOR THE RAT TRACKING PROTOCOL ###


from defs import *
import cv2.cv as cv
import cv2
from syncFiles import *
import numpy as np
import sys


NUM_MICS = 1
WINDOW_NAME = 'Feed'
TOLERANCE = 30


if sys.argv[1] == 'track':
	stimProtocol = False

elif sys.argv[1] == 'protocol':
	stimProtocol = True

else:
	print "ERROR: second argument must be either 'track' or 'protocol'"
	quit()

if len( sys.argv ) > 2:
	INPUT_VID = True
	INPUT_NAME = sys.argv[2]
	

else:
	INPUT_NAME = ""
	INPUT_VID = False



(capture,size) = initializeCapture(INPUT_VID, INPUT_NAME)
NamedWindow(WINDOW_NAME)
MoveWindow(WINDOW_NAME, 610	, 5)
restrainer = {}
rois = []


pickColor(capture, WINDOW_NAME)
restrainer = pickRestrainer(capture, WINDOW_NAME)
print ('restrainer', restrainer)
pickRois(capture, rois, WINDOW_NAME)
if stimProtocol:
	(recordingData) = trackRoisProt(capture,rois,restrainer, WINDOW_NAME, TOLERANCE, writer, NUM_MICS)
else:
	(recordingData) = trackRois(capture,rois,restrainer, WINDOW_NAME, TOLERANCE, writer, NUM_MICS)

#sync(recordingData, NUM_MICS)