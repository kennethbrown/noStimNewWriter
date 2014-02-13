### CONTAINS MOST FUNCTIONS CALLED FROM THE MAIN TRACK.PY SCRIPT ###

from cv2.cv import *
import cv2
from cv import *
from writer import *
from Master8 import *
from scipy import *
from scipy.cluster import vq
import numpy
import sys, os, random, hashlib
import Image
import time
import math
from audio import *
from stimulate import *
from stimProtocol import *

################################ variable declarations and initializations #######################################################################################################

global drawing, drew, eventr, p1,p2,box_width,box_height, h,s,v,i,r,g,b,j, frame, picked
global sobel, smooth, erode, select, liveTrack, writer

liveTrack = False
sobel = 0
smooth = 0
erode = 0


picked = False
drawing = False 
drew = False 
p1 = (0,0)
p2 = (0,0)
box_width = 0
box_height = 0
h,s,v,i,r,g,b,j = 0,0,0,0,0,0,0,0
select = ''

############################################ settings to be modified #######################################################################################################


INACTIVE_LIMIT = 5  #Seconds of inactivity before stimulation
IGNORE_LIMIT = 5     #Seconds of restrainer ignoring before stimulation
WIGGLE_ROOM = 5     #minimum distance, in pixels, for the rat to be considered moving from frame to frame 
SPEED_ACCURACY = 5 	#Number of digits to which speed calculations are rounded to
RESTRAINER_CONSTANT = 5 #Multiplier to define what is considered close to the restrainer (larger number results in larger area)


#############################################################################################################################################################################

FPS = 15 #frame rate for video output file
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
BLUE = (255,0,0)
GREEN = (0,255,0)
RED = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)
FONT = InitFont(CV_FONT_HERSHEY_TRIPLEX  , 0.5,0.5)
ERODE = 1
smooth = 2
SOBEL = 3
OUTPUT_VIDEO = "video out.avi"


writer = cv2.VideoWriter(filename=OUTPUT_VIDEO, 
fourcc=CV_FOURCC('D', 'I', 'V', 'X'), #this is the codec that works for me
fps=FPS, #frames per second, I suggest 15 as a rough initial estimate
frameSize=(400, 600))

#############################################################################################################################################################################

# Mouse callback for picking an ROI #
def roi_callback(event,x,y,flags,param):
	global eventr,p1,p2,drawing,box_width,box_height,drew
	eventr=event
	swapX = False
	swapY = False

	if event==CV_EVENT_LBUTTONDOWN:
		drawing=True
		swapX = False
		swapY = False
		p1 = (x,y)
		p2 = p1

	if event==CV_EVENT_MOUSEMOVE:
		if(drawing):
			box_width=x-p1[0]
			box_height=y-p1[1]

	if event==CV_EVENT_LBUTTONUP:
		drawing = False
		if(box_width < 0):
			box_width *= -1
			swapX=True

		if( box_height < 0 ):
			box_height *= -1
			swapY=True
		p2=(x,y)

		if (swapX and swapY):
			p2 = p1
			p1 = (x,y)
		elif (swapX):
			p2 = (p1[0],p2[1])
			p1 = (x,p1[1])
		elif (swapY):
			p2 = (p2[0],p1[1])
			p1 = (p1[0],y)

		print("P1",p1)
		print("P2",p2)
		drew = True

#############################################################################################################################################################################

# Mouse callback for the start/stop button #
def start_callback(event,x,y,flags,param):
	global liveTrack, frame, writer

	if event == CV_EVENT_LBUTTONDBLCLK:
		liveTrack = not liveTrack
		if liveTrack:
			print 'start'
			width = GetSize(frame)[0]
			height = GetSize(frame)[1]
			writer = cv2.VideoWriter(filename=OUTPUT_VIDEO, 
			fourcc=CV_FOURCC('D', 'I', 'V', 'X'), #this is the codec that works for me
			fps=30, #frames per second, I suggest 15 as a rough initial estimate
			frameSize=(width, height))
			
		else:
			print'stop'

#############################################################################################################################################################################

# Mouse callback for picking a target color #		
def color_callback(event,x,y,flags,param):
	global h,s,v,i,r,g,b,j, picked

	if event==CV_EVENT_LBUTTONDBLCLK:		# Here event is left mouse button double-clicked
		picked = True
		hsv=CreateImage(GetSize(frame),8,3)
		FloodFill(hsv,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		CvtColor(frame,hsv,CV_BGR2HSV)
		(h,s,v,i)=Get2D(hsv,y,x)
		(r,g,b,j)=Get2D(frame,y,x)
		print "x,y =",x,y
		print "hsv= ",Get2D(hsv,y,x)		# Gives you HSV at clicked point
		print "im= ",Get2D(frame,y,x) 	# Gives you RGB at clicked point

#############################################################################################################################################################################


# Mouse callback for the erode window (not being used right now) #
def erode_callback(event,x,y,flags,param):
	global erode, select

	if event==CV_EVENT_LBUTTONDBLCLK:
		select = 'erode'
		print "erode"

#############################################################################################################################################################################

# Mouse callback for the smooth window #
def smooth_callback(event,x,y,flags,param):
	global smooth, select
	if event==CV_EVENT_LBUTTONDBLCLK:
		select = 'smooth'
		print "smooth"

#############################################################################################################################################################################

# Mouse callback for the sobel window (not being used right now) #
def sobel_callback(event,x,y,flags,param):
	global sobel, select
	if event==CV_EVENT_LBUTTONDBLCLK:
		select = 'sobel'
		print "sobel"

#############################################################################################################################################################################

# Mouse callback for the laplace window (not being used right now) #
def laplace_callback(event,x,y,flags,param):
	global sobel, select
	if event==CV_EVENT_LBUTTONDBLCLK:
		select = 'laplace'
		print "laplace"

#############################################################################################################################################################################

# Mouse callback for the median window (not being used right now) #
def median_callback(event,x,y,flags,param):
	global median, select
	if event==CV_EVENT_LBUTTONDBLCLK:
		select = 'median'
		print 'median'

#############################################################################################################################################################################

# returns capture as a video file stream as specified by the command line agrument when the script was called or as a webcam stream
# if no argument was provided #
def initializeCapture(INPUT_VID, INPUT_NAME):
	if INPUT_VID:
		capture = CaptureFromFile( INPUT_NAME )
	
	else:
		#is_color = True
		capture = CaptureFromCAM(0)
		SetCaptureProperty(capture, CV_CAP_PROP_FRAME_WIDTH, FRAME_WIDTH )
		SetCaptureProperty(capture, CV_CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
	frame = QueryFrame(capture)
	size = 0
	if frame:
		size = cv.GetSize(frame)

	return (capture,size)

#############################################################################################################################################################################

# Function for drawing given ROI to given window #
def drawRoi(roi,window,color):
	Line(window,roi['top_left'],roi['top_right'],color,2)
	Line(window,roi['top_left'], roi['bottom_left'],color,2)
	Line(window,roi['top_right'], roi['bottom_right'], color,2)
	Line(window,roi['bottom_left'], roi['bottom_right'], color,2)

#############################################################################################################################################################################

# Allows user to pick out the restrainer on screen #
def pickRestrainer(capture, window):
	global frame 
	key = -1
	chose = False 
	frame = QueryFrame(capture)
	SetMouseCallback(window,roi_callback)
	NamedWindow("Instructions")
	MoveWindow("Instructions", 205,0)
	text = CreateImage((400,60),8,3)
	FloodFill(text, (1,1), Scalar(255,255,255),(1000,10000,1000,10000), (10000,10000,10000,1000))
	PutText(text,"Drag Mouse to Highlight the ", (20, 20), FONT, (0,0,0))
	PutText(text,"Restrainer", (275,20), FONT, (0,0,250))
	PutText(text,"Hit Space when Satisfied then Enter", (20, 40), FONT, (0,0,0))
	while True:
		ShowImage("Instructions", text)
		drawBoard = CreateImage(GetSize(frame),8,3)
		canvas = CreateImage(GetSize(frame),8,3)
		
		FloodFill(canvas,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(drawBoard,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))

		Add(frame,canvas,canvas)
		tempX = p1[0]+box_width
		tempY = p1[1]+box_height
		tempRight = (tempX, p1[1])
		tempDown = (p1[0], tempY)
		tempP2 = (tempX, tempY)

		if(drawing):
			Line(drawBoard,p1, tempRight,RED,2)
			Line(drawBoard,p1, tempDown,RED,2)
			Line(drawBoard,tempDown, tempP2,RED,2)
			Line(drawBoard,tempRight, tempP2,RED,2)

		if(not drawing and drew):
			Rectangle(drawBoard,p1,p2,RED,2)
			if key == 32: ##space
				restrainer = {'top_left': p1, 'bottom_right': p2, 'top_right': tempRight, 'bottom_left': tempDown}
				chose = True

		if (chose):
			color = (0,255,255)
			drawRoi(restrainer, drawBoard, color)

			if key == 13 or key == 27:
				return restrainer

		Add(drawBoard,frame,canvas)
		ShowImage(window,canvas)
		key = WaitKey(33) % 0x100
		

#############################################################################################################################################################################

# Allows user to pick the region in which tracking will be performed (was originally written to support multiple tracking regions
# but the user should only pick one tracking region for our purposes) #
def pickRois(capture, rois, window):
	global frame
	key = -1
	frame = QueryFrame(capture)
	SetMouseCallback(window,roi_callback)
	NamedWindow("Instructions")
	MoveWindow("Instructions", 205,0)
	text = CreateImage((400,60),8,3)
	FloodFill(text, (1,1), Scalar(255,255,255),(1000,10000,1000,10000), (10000,10000,10000,1000))
	PutText(text,"Drag Mouse to Highlight the ", (20, 20), FONT, (0,0,0))
	PutText(text,"Arena", (275,20), FONT, (250,0,0))
	PutText(text,"Hit Space when Satisfied then Enter", (20, 40), FONT, (0,0,0))
	
	while True:
		ShowImage("Instructions", text)
		drawBoard = CreateImage(GetSize(frame),8,3)
		canvas = CreateImage(GetSize(frame),8,3)
		FloodFill(drawBoard,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(canvas,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		Add(frame,canvas,canvas)
		tempX = p1[0]+box_width
		tempY = p1[1]+box_height
		tempRight = (tempX, p1[1])
		tempDown = (p1[0], tempY)
		tempP2 = (tempX, tempY)

		if(drawing):
			Line(drawBoard,p1, tempRight,BLUE,2)
			Line(drawBoard,p1, tempDown,BLUE,2)
			Line(drawBoard,tempDown, tempP2,BLUE,2)
			Line(drawBoard,tempRight, tempP2,BLUE,2)
			

		if(not drawing and drew):
			Rectangle(drawBoard,p1,p2,BLUE,2)
			if key == 32:  ###space
				tempRoi = {'top_left': p1, 'bottom_right': p2, 'top_right': tempRight, 'bottom_left': tempDown}
				rois.append(tempRoi)

		for roi in rois:
			drawRoi(roi, drawBoard, GREEN)

		Add(drawBoard,frame,canvas)
		ShowImage(window, canvas)
		key = WaitKey(33) % 0x100

		if key == 13 or key == 27: ###enter or esc
			if len(rois)>0:
				break

#############################################################################################################################################################################


# Allows user to pick a target color to track #
def pickColor(capture, window):
	global frame
	key = -1
	frame = QueryFrame(capture)
	SetMouseCallback(window,color_callback)
	NamedWindow("Instructions")
	MoveWindow("Instructions", 205,0)
	text = CreateImage((400,30),8,3)
	FloodFill(text, (1,1), Scalar(255,255,255),(1000,10000,1000,10000), (10000,10000,10000,1000))
	PutText(text,"Double Click Target Color and Press Enter", (10, 20), FONT, (0,0,0))


	while True:
		ShowImage("Instructions", text)
		ShowImage(window,frame)
		key = WaitKey(33) % 0x100
		if picked:
			if key == 13 or key == 27: ###enter or esc
				break 


#############################################################################################################################################################################

# takes a given image and thresholds it according to a target color (specified by the tuple 'colors'). Threshold tolerance is 
# determined by 'tolerance' #		
def threshold(image, mode, colors, tolerance):
	if mode == 'hsv':
		h = colors[0]
		s = colors[1]
		v = colors[2]
		imghsv= CreateImage(GetSize(image),8,3)
		FloodFill(imghsv,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		CvtColor(image,imghsv,CV_BGR2HSV)
		imageOut = CreateImage(GetSize(image),8,1)
		FloodFill(imageOut,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))

		InRangeS(imghsv,Scalar(h-tolerance,s-tolerance,v-tolerance),Scalar(h+tolerance,s+tolerance, v+tolerance),imageOut)
		return imageOut

	if mode == 'rgb':
		r = colors[0]
		g = colors[1]
		b = colors[2]
		imageOut = CreateImage(GetSize(image),8,1)
		FloodFill(imageOut,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		InRangeS(image,Scalar(r-tolerance,g-tolerance,b-tolerance),Scalar(r+tolerance,g+tolerance, b+tolerance),imageOut)
		return imageOut

	else:
		print ("ERROR, PICK A CORRECT MODE")


#############################################################################################################################################################################

# filters a thresholded image using the filters specified by 'params'. Though it supports multiple filters, the script is
# currently only using the 'smooth' filter #
def imageFilter(image, params):

	if 'erode' in params:
		erode = params['erode']		
	 	if erode > 0:
	 		Erode(image,image,None,erode)

	if 'sobel' in params:
		sobel = params['sobel']
	 	if sobel > 0 and sobel < 3:
	 		Sobel(image,image,sobel,sobel)

	if 'median' in params:
		median = params['median']
		if median % 2 == 0:
			median += 1
		if median > 0:
			Smooth(image,image, smoothtype = CV_MEDIAN, param1 = median, param2 = median, param3=5, param4=5)


	if 'smooth' in params:
		smooth = params['smooth']

		if smooth % 2 == 0:
			smooth += 1
		if smooth > 0:
			Smooth(image,image, smoothtype = CV_BLUR, param1 = smooth, param2 = smooth, param3=5, param4=5)


	if 'laplace' in params:
		laplace = params['laplace']		
		if laplace > 0 and laplace < 3:
			Laplace(image,image)

#############################################################################################################################################################################

# finds the location of the restrainer rat (returned as restrainerPoint) and the arena rat (returned as arenaPoint) of a given image, which
# is assumed to already have been thresholded and filtered. Returns time stamps measuring both (in)activity and restrainer approach #
def track(image, roi, restrainer, liveTrack, active, inRestrainer, p0, nearRestrainer, timeTracker, recording, NUM_MICS, outputVideo):

	globalTime = time.clock()
	T0 = timeTracker[0]
	timeElapsed = timeTracker[1]
	inactiveT0 = timeTracker[2]
	inactiveElapsed = timeTracker[3]
	approachT0 = timeTracker[4]
	approachElapsed = timeTracker[5]
	ignoreT0 = timeTracker[6]
	ignoreElapsed = timeTracker[7]

	restTopLeft = (restrainer['top_left'][0]-roi['top_left'][0],restrainer['top_left'][1]-roi['top_left'][1])
	restTopRight = (restrainer['top_right'][0]-roi['top_right'][0],restrainer['top_right'][1]-roi['top_right'][1])
	restBottomLeft = (restrainer['bottom_left'][0]-roi['bottom_left'][0],restrainer['bottom_left'][1]-roi['bottom_left'][1])
	restBottomRight = (restrainer['bottom_right'][0]-roi['bottom_right'][0],restrainer['bottom_right'][1]-roi['bottom_right'][1])

	arenaArray = numpy.asarray(GetMat(image))
	restrainerArray = numpy.copy(arenaArray)
	arenaArray[restTopLeft[1]:restBottomLeft[1], restTopLeft[0]:restTopRight[0]].fill(0)


	restrainerArray[0:restTopLeft[1],0:GetSize(image)[0]].fill(0)
	restrainerArray[restBottomLeft[1]:GetSize(image)[1],0:GetSize(image)[0]].fill(0)
	restrainerArray[0:GetSize(image)[1],0:restTopLeft[0]].fill(0)
	restrainerArray[0:GetSize(image)[1],restTopRight[0]:GetSize(image)[0]].fill(0)




	sumX = arenaArray.sum(0)
	sumY = arenaArray.sum(1)

	i = 0
	j = 0
	maxX = -1
	maxY = -1
	indexX = -2
	indexY = -2

	while (i < sumX.size or j < sumY.size):

		if i < sumX.size:

			tempX = sumX[i]
			if tempX > maxX and tempX > 0:
				maxX = tempX
				indexX = i
			i += 1
		
		if j < sumY.size:
			tempY = sumY[j]
			if tempY > maxY and tempY > 0:
				maxY = tempY
				indexY = j
			j += 1

	x = indexX + roi['top_left'][0]
	y = indexY + roi['top_left'][1]
	arenaPoint = (x, y)


	sumX = restrainerArray.sum(0)
	sumY = restrainerArray.sum(1)

	i = 0
	j = 0
	maxX = -1
	maxY = -1
	indexX = -2
	indexY = -2

	while (i < sumX.size or j < sumY.size):

		if i < sumX.size:
			tempX = sumX[i]
			if tempX > maxX and tempX > 0:
				maxX = tempX
				indexX = i
			i += 1
		
		if j < sumY.size:
			tempY = sumY[j]
			if tempY > maxY and tempY > 0:
				maxY = tempY
				indexY = j

			j += 1

	x = indexX + roi['top_left'][0]
	y = indexY + roi['top_left'][1]
	restrainerPoint = (x, y)

	if abs(arenaPoint[0]-p0[0]) < WIGGLE_ROOM and abs(arenaPoint[1]-p0[1]) < WIGGLE_ROOM:
		active = False
	else:
		active = True

	if arenaPoint[0] > nearRestrainer['top_left'][0] and arenaPoint[0] < nearRestrainer['top_right'][0]:
		if arenaPoint[1] > nearRestrainer['top_left'][1] and arenaPoint[1] < nearRestrainer['bottom_left'][1]:
			inRestrainer = True
		else:
			inRestrainer = False

	else:
		inRestrainer = False



	currentTime = time.clock()

	if NUM_MICS == 0:
		frequencyai0 = 'NA'
		frequencyai1 = 'NA'
		recordTime = 'NA'

	elif NUM_MICS == 1:
		frequencyai0 = recording.data[0]
		frequencyai1 = 'NA'
		# if len(recording.data) == 0:
			# recordTime = 0
		# else:
			# recordTime = max(recording.timeStamps[len(recording.timeStamps)-1][1],0)
		recordTime = 0
			
	elif NUM_MICS == 2:
		tempFreq = recording.readAll()
		# print tempFreq
		frequencyai0 = tempFreq['Dev2/ai0'][0]
		frequencyai1 = tempFreq['Dev2/ai1'][0]

		recordTime = tempFreq['Dev2/ai0'][1]
		# if len(recordingai0.timeStamps) == 0:
		# 	recordTime = 0
		# else:
		# 	recordTime = max(recordingai0.timeStamps[len(recordingai0.timeStamps)-1][1],0)
		

	if not liveTrack:
		T0 = time.clock()
		timeElapsed = 0
		ignoreElapsed = 0
		approachElapsed = 0
		inactiveElapsed = 0
		inactiveT0 = time.clock()
		approachT0 = time.clock()
		ignoreT0 = time.clock()

	elif liveTrack:
		timeElapsed = currentTime - T0

		if active:
			inactiveT0 = time.clock()
			inactiveElapsed = 0
		elif not active:
			inactiveElapsed = currentTime - inactiveT0

		if not inRestrainer:
			approachT0 = time.clock()
			approachElapsed = 0
			ignoreElapsed = currentTime - ignoreT0
		elif inRestrainer:
			approachElapsed = currentTime - approachT0
			ignoreT0 = time.clock()
			ignoreElapsed = 0



	timeTuple = (T0, timeElapsed , inactiveT0 , inactiveElapsed , 
				approachT0, approachElapsed, ignoreT0, ignoreElapsed)

	return (arenaPoint,restrainerPoint,active,inRestrainer,timeElapsed,timeTuple,globalTime, frequencyai0, frequencyai1, recordTime)
	

#############################################################################################################################################################################

# calculates speed, in pixels per second, given two locations and the time elapsed between the two location #
def findSpeed(p0, p1, deltaT):
	p0 = (float(p0[0]),float(p0[1]))
	p1 = (float(p1[0]),float(p1[1]))
	distance = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
	speed = round((distance/deltaT), SPEED_ACCURACY)
	return speed


#############################################################################################################################################################################

# tracks the rats in the given rois (tracking regions). Currently being used only on one tracking region. If the user
# has started the tracking protocol, writes frames to a video avi file and tracking data to a csv file. Also records 
# audio signal via a DAQ board #
def trackRois(capture, rois, restrainer, window, tolerance, outputVideo, NUM_MICS):
	global liveTrack, frame, writer


	NamedWindow("Instructions")
	MoveWindow("Instructions", 205,0)
	text = CreateImage((400,60),8,3)
	FloodFill(text, (1,1), Scalar(255,255,255),(1000,10000,1000,10000), (10000,10000,10000,1000))
	PutText(text,"Double Click \"Start\\Stop\" to turn ", (20, 20), FONT, (0,0,0))
	PutText(text,"tracking on or off", (20,40), FONT, (0,0,0))

	filterParams = {"smooth":45}
	NamedWindow("start/stop")
	MoveWindow("start/stop", 205, 90)
	# NamedWindow("erode")
	NamedWindow("smooth")
	MoveWindow("smooth",410,90)
	NamedWindow("display")
	MoveWindow("display", 0,0)
	# # NamedWindow("sobel")
	# NamedWindow("laplace")
	# NamedWindow("median")
	# SetMouseCallback("erode", erode_callback)
	SetMouseCallback("smooth", smooth_callback)
	# # SetMouseCallback("sobel", sobel_callback)
	# SetMouseCallback("laplace", laplace_callback)
	# SetMouseCallback("median", median_callback)
	SetMouseCallback("start/stop", start_callback)
	displayImage =  CreateImage((200,960),8,3)
	startImage = CreateImage((200,25),8,3)
	# NamedWindow("Track Map")

	
	
	inRestrainer = False
	liveTrack = False
	active = False
	p0 = (0,0)
	nearRestrainer = False
	T0 = 0
	timeElapsed = 0
	inactiveT0 = 0
	inactiveElapsed = 0
	approachT0 = 0
	approachElapsed = 0
	ignoreT0 = 0
	ignoreElapsed = 0
	timeTracker = (T0, timeElapsed, inactiveT0, inactiveElapsed, approachT0, approachElapsed, ignoreT0, ignoreElapsed)
	arenaPoint = (0,0)
	restrainerPoint = (0,0)
	stimulate = False
	# stimulator = Master8()
	stimulator = 'stimulator'
	# stimulator.changeChannelMode(1,OFF)
	duration = DURATION * (.001)
	# delay = DELAY *(.001)
	interval = INTERVAL * (.001)
	# stimulator.setChannelDuration(1,duration)
	# stimulator.setChannelDelay(1,delay)
	# stimulator.setChannelInterval(1,interval)
	# stimulator.setChannelM(1,NUM_PULSES)
	# stimulateOff()
	angle = 0
	speed = 0
	timeStamp = 0
	firstLine = True
	stimStart = 0
	stimTime = 0
	stimEnd = 0
	offTime = 0


	if NUM_MICS == 0:
		recording = " "

	elif NUM_MICS == 1:
		recording = Record()
		recordingData = []
		recording.StartTask()

	elif NUM_MICS == 2:
		recording =  MultiRecord(["Dev2/ai0","Dev2/ai1"])
		recording.configure()
		recordingData = {'ai0':[], 'ai1':[]}

	# recordingai1.StartTask()
	frame = QueryFrame(capture)
	print type(frame)

	while True:
	
	######################################### Filter Boxes ####################################	
		ShowImage("Instructions", text)
		frame = QueryFrame(capture)
		# vidFrame = capture.read()
		canvas = CreateImage(GetSize(frame),8,3)
		thresh_img = CreateImage(GetSize(frame),8,1)
		query = CreateImage(GetSize(frame),8,3)
		# imdraw = CreateImage((rois[0]['top_right'][0] - rois[0]['top_left'][0], rois[0]['bottom_left'][1] - rois[0]['top_left'][1]),8,3)
		FloodFill(canvas,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(query,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(thresh_img,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(startImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		Add(canvas,frame,canvas)
		Add(query, frame, query)

		lastStimulate = stimulate
		# erodeImage = CreateImage((200,25),8,3)
		smoothImage = CreateImage((195,25),8,3)
		# sobelImage = CreateImage((200,25),8,3)
		# laplaceImage = CreateImage((200,25),8,3)
		# medianImage = CreateImage((200,25),8,3)
		FloodFill(displayImage,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(erodeImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(smoothImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(sobelImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(laplaceImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(medianImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# if 'erode' in filterParams:
			# PutText(erodeImage, str(filterParams['erode']), (5,15), FONT, Scalar(250,250,250))
		if 'smooth' in filterParams:
			PutText(smoothImage, str(filterParams['smooth']), (5,15), FONT, Scalar(250,250,250))
		# if 'sobel' in filterParams:
			# PutText(sobelImage, str(filterParams['sobel']), (5,15), FONT, Scalar(250,250,250))
		# if 'laplace' in filterParams:
			# PutText(laplaceImage, str(filterParams['laplace']), (5,15), FONT, Scalar(250,250,250))
		# if 'median' in filterParams:
			# PutText(medianImage, str(filterParams['median']), (5,15), FONT, Scalar(250,250,250))
		# ShowImage('erode',erodeImage)
		ShowImage('smooth',smoothImage)
		# ShowImage('sobel',sobelImage)
		# ShowImage('laplace', laplaceImage)
		# ShowImage('median', medianImage)
		if liveTrack:
			startText = "Stop Tracking"
			startColor = RED
		else:
			startText = "Start Tracking"
			startColor = GREEN

		PutText(startImage, startText, (30,15), FONT, startColor)
		ShowImage('start/stop', startImage)







	##############################################################################################	
								# Draw Restrainer Region #
		tempImage = CreateImage(GetSize(frame),8,3)
		FloodFill(tempImage,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		#restrainer = {'top_left': p1, 'bottom_right': p2, 'top_right': tempRight, 'bottom_left': tempDown}
		addX = abs(restrainer['top_left'][0]-restrainer['top_right'][0]) / RESTRAINER_CONSTANT
		addY = abs(restrainer['top_left'][1] - restrainer['bottom_left'][1]) / RESTRAINER_CONSTANT
		if addX > addY:
			addY = addX
		elif addY > addX:
			addX = addY
		tempTopLeft = (restrainer['top_left'][0] - addX, restrainer['top_left'][1] - addY)
		tempTopRight = (restrainer['top_right'][0] + addX, restrainer['top_right'][1] - addY)
		tempBottomLeft = (restrainer['bottom_left'][0] - addX, restrainer['bottom_left'][1] + addY)
		tempBottomRight = (restrainer['bottom_right'][0] + addX, restrainer['bottom_right'][1] + addY)
		nearRestrainer = {'top_left': tempTopLeft, 'top_right': tempTopRight, 'bottom_left': tempBottomLeft, 'bottom_right':tempBottomRight}

		Rectangle(canvas,restrainer['top_left'], restrainer['bottom_right'], (50,0,50),1)  #restrainer outline
		Rectangle(tempImage,nearRestrainer['top_left'], nearRestrainer['bottom_right'],(0,50,0),-1)  #restrainer ROI area
		
		






################################################################################
		# x1 = restrainer['top_left'][0]
		# x2 = restrainer['top_right'][0]
		# y1 = restrainer['top_left'][1]
		# y2 = restrainer['bottom_right'][1]
		# #searchRegion = (x1,x2,y1,y2)
		# searchRegion = query[y1:y2,x1:x2]
		# FloodFill(searchRegion,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# #Add(thresh_img, frame, thresh_img)
################################################################################

################################################################################
		i=0
		for roi in rois: 
			drawRoi(roi, canvas, BLACK)
			x1 = roi['top_left'][0]
			x2 = roi['top_right'][0]
			y1 = roi['top_left'][1]
			y2 = roi['bottom_right'][1]
			#searchRegion = (x1,x2,y1,y2)
			searchRegion = query[y1:y2,x1:x2]
			colors = (r,g,b)
			imageOut = threshold(searchRegion, 'rgb', colors, tolerance)

			imageFilter(imageOut, filterParams)
			



			string = str(i)
			NamedWindow(string)
			i+=1
			#Add(thresh_region, canvas, canvas)
			ShowImage(string,imageOut)
			MoveWindow(string,205,150)



		key = WaitKey(7) #% 0x100
		if key == 27 or key == 13:
			break

		if key == 119: #w
			if select in filterParams:
				temp = filterParams[select] 
			else: 
				temp = 0
			temp += 1
			filterParams.update({select:temp})

		if key == 115: #s
			if select in filterParams:
				temp = filterParams[select] 
			else: 
				temp = 0
			if temp > 0:
				temp -= 1
			filterParams.update({select:temp})

		if key >=48 and key < 115: ####number entery
			tempInt = key - 48

			filterParams.update({select:tempInt})
			



################################################################################
		######OBJECT TRACKING##########


		p0 = (arenaPoint[0], arenaPoint[1])
		lastTime = timeElapsed
		p0 = (arenaPoint[0], arenaPoint[1])
		(arenaPoint,restrainerPoint,active,inRestrainer,timeElapsed, timeTracker,timeStamp, audioFreqai0, audioFreqai1, audioTime) = track(imageOut, 
			rois[0], restrainer, liveTrack, active, inRestrainer, p0, nearRestrainer, timeTracker, recording, NUM_MICS, outputVideo)

		if NUM_MICS == 2:
			recordingData['ai0'].append((audioFreqai0,audioTime)) 
			recordingData['ai1'].append((audioFreqai1,audioTime))

		T0 = timeTracker[0]
		timeElapsed = timeTracker[1]
		inactiveT0 = timeTracker[2]
		inactiveElapsed = timeTracker[3]
		approachT0 = timeTracker[4]
		approachElapsed = timeTracker[5]
		ignoreT0 = timeTracker[6]
		ignoreElapsed = timeTracker[7]

		

		
		Circle(canvas,arenaPoint,5,(0,255,0),-1)
		Circle(canvas,restrainerPoint,5,(255,0,0),-1)


		if liveTrack:
			deltaT = timeElapsed - lastTime
			if timeElapsed > 1:
				speed = findSpeed(p0, arenaPoint, deltaT)
				firstLine = False
				stimulate = False
				if ignoreElapsed > IGNORE_LIMIT:
					stimulate = True
					(stimStart, stimTime, stimEnd, offTime) = stimulateOn(lastStimulate, stimulator, stimStart)
					# stimulateOn()
				if inactiveElapsed > INACTIVE_LIMIT and not inRestrainer:
					stimulate = True
					(stimStart, stimTime, stimEnd, offTime) = stimulateOn(lastStimulate, stimulator, stimStart)
					# stimulateOn()
				if not stimulate:
					(stimStart, stimTime, stimEnd, offTime) = stimulateOff(lastStimulate, stimulator, stimEnd)
				
			else:
				speed = 0
				firstLine = True
				stimulate = False
				(stimStart, stimTime, stimEnd, offTime) = stimulateOff(lastStimulate, stimulator, stimEnd)
				# stimulateOff()

			if stimulate:
				if (int(stimTime) % TRIGGER_WAIT) == 0:
					# stimulator.trigger(1)
					print 'stim'

			# timeStamp = timeElapsed

			writeToFile(arenaPoint,timeElapsed,angle,speed,active,inactiveElapsed,inRestrainer,approachElapsed,ignoreElapsed,
						stimulate,firstLine,timeStamp)
			# print recording.data[0]
			# audioFreq, audioTime



			

			trackText = "Tracking"
			if active:
				activeText = "active"
				activeColor = GREEN
			else:
				activeText = "Inactive"
				activeColor = RED

			if inRestrainer:
				restrainerText =  "Approaching"
				restrainerColor = GREEN
				approachText = str(round(approachElapsed,5))

			else:
				restrainerText = "Ignoring"
				restrainerColor = RED
				approachText = str(round(ignoreElapsed,5))

			if stimulate:
				stimulateText =  "STIMULATE"
				stimulateColor = BLUE
			else:
				stimulateText = "DONT STIMULATE"
				stimulateColor = (255,255,0)

			elapsedText = str(round(timeElapsed,5))
			
			inactiveText = str(round(inactiveElapsed,5))
			audioColor = GREEN





		else:
			speed = -1
			stimulate = False
			stimulateOff(lastStimulate, stimulator, stimEnd)
			# stimulateOff()
			trackText = "Not Tracking"
			activeText = "Not Tracking"
			restrainerText = "Not Tracking"
			activeColor = WHITE
			activeColor = WHITE
			restrainerColor = WHITE
			elapsedText = "Not Tracking"
			approachText = "Not Tracking"
			inactiveText = "Not Tracking"
			stimulateText = "Not Tracking"
			stimulateColor = WHITE
			audioColor = WHITE

		audioTextai0 = str(audioFreqai0)
		audioTextai1 = str(audioFreqai1)

		PutText(displayImage, "Track Status: " , (5,15), FONT, Scalar(250,250,250))
		PutText(displayImage, trackText, (25,35), FONT, Scalar(250,250,250))
		PutText(displayImage, "Activity: " , (5,65), FONT, activeColor)
		PutText(displayImage, activeText, (25,85), FONT, activeColor)
		PutText(displayImage, "Location: " , (5,115), FONT, WHITE)
		PutText(displayImage,  str(arenaPoint), (25,135), FONT, WHITE)
		PutText(displayImage, "Restrainer Approach: " , (5,165), FONT, restrainerColor)
		PutText(displayImage, restrainerText, (25,185), FONT, restrainerColor)

		PutText(displayImage, "Time Elapsed: " , (5,255), FONT, Scalar(250,250,250))
		PutText(displayImage, elapsedText, (25,275), FONT, Scalar(250,250,250))
		if inRestrainer and liveTrack:
			PutText(displayImage, "Approach ", (5,305), FONT, GREEN)
			PutText(displayImage, "Elapsed: " , (90,305), FONT, Scalar(250,250,250))
		elif not inRestrainer and liveTrack:
			PutText(displayImage, "Ignore ", (5,305), FONT, RED)
			PutText(displayImage, "Elapsed: " , (68,305), FONT, Scalar(250,250,250))
		else:
			PutText(displayImage, "Approach Elapsed: ", (5,305), FONT, WHITE)
		PutText(displayImage, approachText, (25,325), FONT, restrainerColor)
		PutText(displayImage, "Inactive Elapsed: " , (5,355), FONT, Scalar(250,250,250))
		PutText(displayImage, inactiveText, (25,375), FONT, Scalar(250,250,250))
		PutText(displayImage, "Stimulator Status: ", (5, 405), FONT, WHITE)
		PutText(displayImage, stimulateText, (25,425), FONT, stimulateColor)
		PutText(displayImage, "Audio Signal ai0: ", (5, 455), FONT, WHITE)
		PutText(displayImage, audioTextai0, (25,475), FONT, audioColor)
		PutText(displayImage, "Audio Signal ai1: ", (5, 505), FONT, WHITE)
		PutText(displayImage, audioTextai1, (25,525), FONT, audioColor)
		if stimulate and liveTrack:
			if round(time.clock(),0) % 2 == 0:
				PutText(tempImage, "Stimulating", (nearRestrainer['top_left'][0]+13, nearRestrainer['top_left'][1]+20), FONT, (255,255,0))








		ShowImage("display",displayImage)

		Add(tempImage,canvas,canvas)
		if liveTrack:
			# tempFrame = numpy.asarray(GetMat(frame))   ############ Uncomment To write unedited Frame
			tempFrame = numpy.asarray(GetMat(canvas))    ############ Uncomment To Write Tracking Frame

			writer.write(tempFrame)

		
		ShowImage(window, canvas)


	if NUM_MICS == 0:
		recordingData = " "

	elif NUM_MICS == 1:
		recording.StopTask()
        for thr in recording.threads:
            thr.join()
        recording.ClearTask()
		#recordingData = recording.timeStamps



		
	# recordingai1.StopTask()
	# recordingai1.ClearTask()

	return (recording)



#############################################################################################################################################################################

def trackRoisProt(capture, rois, restrainer, window, tolerance, outputVideo, NUM_MICS):
	global liveTrack, frame, writer


	NamedWindow("Instructions")
	MoveWindow("Instructions", 205,0)
	text = CreateImage((400,60),8,3)
	FloodFill(text, (1,1), Scalar(255,255,255),(1000,10000,1000,10000), (10000,10000,10000,1000))
	PutText(text,"Double Click \"Start\\Stop\" to turn ", (20, 20), FONT, (0,0,0))
	PutText(text,"tracking on or off", (20,40), FONT, (0,0,0))

	filterParams = {"smooth":45}
	NamedWindow("start/stop")
	MoveWindow("start/stop", 205, 90)
	# NamedWindow("erode")
	NamedWindow("smooth")
	MoveWindow("smooth",410,90)
	NamedWindow("display")
	MoveWindow("display", 0,0)
	# # NamedWindow("sobel")
	# NamedWindow("laplace")
	# NamedWindow("median")
	# SetMouseCallback("erode", erode_callback)
	SetMouseCallback("smooth", smooth_callback)
	# # SetMouseCallback("sobel", sobel_callback)
	# SetMouseCallback("laplace", laplace_callback)
	# SetMouseCallback("median", median_callback)
	SetMouseCallback("start/stop", start_callback)
	displayImage =  CreateImage((200,960),8,3)
	startImage = CreateImage((200,25),8,3)
	# NamedWindow("Track Map")

	
	
	inRestrainer = False
	liveTrack = False
	active = False
	p0 = (0,0)
	nearRestrainer = False
	T0 = 0
	timeElapsed = 0
	inactiveT0 = 0
	inactiveElapsed = 0
	approachT0 = 0
	approachElapsed = 0
	ignoreT0 = 0
	ignoreElapsed = 0
	timeTracker = (T0, timeElapsed, inactiveT0, inactiveElapsed, approachT0, approachElapsed, ignoreT0, ignoreElapsed)
	arenaPoint = (0,0)
	restrainerPoint = (0,0)
	stimulate = False
	# stimulator = Master8()
	stimulator = 'stimulator'
	# stimulator.changeChannelMode(protChannel,OFF)
	duration = protDuration * (.001)
	# delay = DELAY *(.001)
	interval = protInterval * (.001)
	# stimulator.setChannelDuration(protChannel,duration)
	# stimulator.setChannelDelay(1,delay)
	# stimulator.setChannelInterval(protChannel,interval)
	# stimulator.setChannelM(protChannel,protNumPulses)
	# stimulateOff()
	angle = 0
	speed = 0
	timeStamp = 0
	firstLine = True
	stimStart = 0
	stimTime = protStimOn + 1
	stimEnd = 0
	offTime = protStimOff + 1


	if NUM_MICS == 0:
		recording = " "

	elif NUM_MICS == 1:
		recording = Record()
		recordingData = []
		recording.StartTask()

	elif NUM_MICS == 2:
		recording =  MultiRecord(["Dev2/ai0","Dev2/ai1"])
		recording.configure()
		recordingData = {'ai0':[], 'ai1':[]}

	# recordingai1.StartTask()
	frame = QueryFrame(capture)
	

	while True:
	
	######################################### Filter Boxes ####################################	
		ShowImage("Instructions", text)
		frame = QueryFrame(capture)
		# vidFrame = capture.read()
		canvas = CreateImage(GetSize(frame),8,3)
		thresh_img = CreateImage(GetSize(frame),8,1)
		query = CreateImage(GetSize(frame),8,3)
		# imdraw = CreateImage((rois[0]['top_right'][0] - rois[0]['top_left'][0], rois[0]['bottom_left'][1] - rois[0]['top_left'][1]),8,3)
		FloodFill(canvas,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(query,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(thresh_img,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(startImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		Add(canvas,frame,canvas)
		Add(query, frame, query)

		lastStimulate = stimulate
		# erodeImage = CreateImage((200,25),8,3)
		smoothImage = CreateImage((195,25),8,3)
		# sobelImage = CreateImage((200,25),8,3)
		# laplaceImage = CreateImage((200,25),8,3)
		# medianImage = CreateImage((200,25),8,3)
		FloodFill(displayImage,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(erodeImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		FloodFill(smoothImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(sobelImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(laplaceImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# FloodFill(medianImage,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# if 'erode' in filterParams:
			# PutText(erodeImage, str(filterParams['erode']), (5,15), FONT, Scalar(250,250,250))
		if 'smooth' in filterParams:
			PutText(smoothImage, str(filterParams['smooth']), (5,15), FONT, Scalar(250,250,250))
		# if 'sobel' in filterParams:
			# PutText(sobelImage, str(filterParams['sobel']), (5,15), FONT, Scalar(250,250,250))
		# if 'laplace' in filterParams:
			# PutText(laplaceImage, str(filterParams['laplace']), (5,15), FONT, Scalar(250,250,250))
		# if 'median' in filterParams:
			# PutText(medianImage, str(filterParams['median']), (5,15), FONT, Scalar(250,250,250))
		# ShowImage('erode',erodeImage)
		ShowImage('smooth',smoothImage)
		# ShowImage('sobel',sobelImage)
		# ShowImage('laplace', laplaceImage)
		# ShowImage('median', medianImage)
		if liveTrack:
			startText = "Stop Tracking"
			startColor = RED
		else:
			startText = "Start Tracking"
			startColor = GREEN

		PutText(startImage, startText, (30,15), FONT, startColor)
		ShowImage('start/stop', startImage)







	##############################################################################################	
								# Draw Restrainer Region #
		tempImage = CreateImage(GetSize(frame),8,3)
		FloodFill(tempImage,(1,1),Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		#restrainer = {'top_left': p1, 'bottom_right': p2, 'top_right': tempRight, 'bottom_left': tempDown}
		addX = abs(restrainer['top_left'][0]-restrainer['top_right'][0]) / RESTRAINER_CONSTANT
		addY = abs(restrainer['top_left'][1] - restrainer['bottom_left'][1]) / RESTRAINER_CONSTANT
		if addX > addY:
			addY = addX
		elif addY > addX:
			addX = addY
		tempTopLeft = (restrainer['top_left'][0] - addX, restrainer['top_left'][1] - addY)
		tempTopRight = (restrainer['top_right'][0] + addX, restrainer['top_right'][1] - addY)
		tempBottomLeft = (restrainer['bottom_left'][0] - addX, restrainer['bottom_left'][1] + addY)
		tempBottomRight = (restrainer['bottom_right'][0] + addX, restrainer['bottom_right'][1] + addY)
		nearRestrainer = {'top_left': tempTopLeft, 'top_right': tempTopRight, 'bottom_left': tempBottomLeft, 'bottom_right':tempBottomRight}

		Rectangle(canvas,restrainer['top_left'], restrainer['bottom_right'], (50,0,50),1)  #restrainer outline
		Rectangle(tempImage,nearRestrainer['top_left'], nearRestrainer['bottom_right'],(0,50,0),-1)  #restrainer ROI area
		
		






################################################################################
		# x1 = restrainer['top_left'][0]
		# x2 = restrainer['top_right'][0]
		# y1 = restrainer['top_left'][1]
		# y2 = restrainer['bottom_right'][1]
		# #searchRegion = (x1,x2,y1,y2)
		# searchRegion = query[y1:y2,x1:x2]
		# FloodFill(searchRegion,(1,1), Scalar(0,0,0),(1000,10000,1000,10000), (10000,10000,10000,1000))
		# #Add(thresh_img, frame, thresh_img)
################################################################################

################################################################################
		i=0
		for roi in rois: 
			drawRoi(roi, canvas, BLACK)
			x1 = roi['top_left'][0]
			x2 = roi['top_right'][0]
			y1 = roi['top_left'][1]
			y2 = roi['bottom_right'][1]
			#searchRegion = (x1,x2,y1,y2)
			searchRegion = query[y1:y2,x1:x2]
			colors = (r,g,b)
			imageOut = threshold(searchRegion, 'rgb', colors, tolerance)

			imageFilter(imageOut, filterParams)
			



			string = str(i)
			NamedWindow(string)
			i+=1
			#Add(thresh_region, canvas, canvas)
			ShowImage(string,imageOut)
			MoveWindow(string,205,150)



		key = WaitKey(7) #% 0x100
		if key == 27 or key == 13:
			break

		if key == 119: #w
			if select in filterParams:
				temp = filterParams[select] 
			else: 
				temp = 0
			temp += 1
			filterParams.update({select:temp})

		if key == 115: #s
			if select in filterParams:
				temp = filterParams[select] 
			else: 
				temp = 0
			if temp > 0:
				temp -= 1
			filterParams.update({select:temp})

		if key >=48 and key < 115: ####number entry
			tempInt = key - 48

			filterParams.update({select:tempInt})
			



################################################################################
		######OBJECT TRACKING##########


		p0 = (arenaPoint[0], arenaPoint[1])
		lastTime = timeElapsed
		p0 = (arenaPoint[0], arenaPoint[1])
		(arenaPoint,restrainerPoint,active,inRestrainer,timeElapsed, timeTracker,timeStamp, audioFreqai0, audioFreqai1, audioTime) = track(imageOut, 
			rois[0], restrainer, liveTrack, active, inRestrainer, p0, nearRestrainer, timeTracker, recording, NUM_MICS, outputVideo)

		if NUM_MICS == 2:
			recordingData['ai0'].append((audioFreqai0,audioTime)) 
			recordingData['ai1'].append((audioFreqai1,audioTime))

		T0 = timeTracker[0]
		timeElapsed = timeTracker[1]
		inactiveT0 = timeTracker[2]
		inactiveElapsed = timeTracker[3]
		approachT0 = timeTracker[4]
		approachElapsed = timeTracker[5]
		ignoreT0 = timeTracker[6]
		ignoreElapsed = timeTracker[7]

		

		
		Circle(canvas,arenaPoint,5,(0,255,0),-1)
		Circle(canvas,restrainerPoint,5,(255,0,0),-1)


		if liveTrack:
			deltaT = timeElapsed - lastTime
			if timeElapsed > 1:
				speed = findSpeed(p0, arenaPoint, deltaT)
				firstLine = False
				# stimulate = False
				tempStimulate = stimulate
				if stimulate == False:
					# print ('Off', offTime)
					(stimStart, stimTime, stimEnd, offTime) = stimulateOff(lastStimulate, stimulator, stimEnd)
					if offTime > protStimOff:
						(stimStart, stimTime, stimEnd, offTime) = stimulateOn(lastStimulate, stimulator, stimStart)
						tempStimulate = True
					# (stimStart, stimTime, stimEnd, offTime) = stimulateOn(lastStimulate, stimulator, stimStart)
					# stimulateOn()
				elif stimulate == True: 
					# print ('stimulating', stimTime)
					(stimStart, stimTime, stimEnd, offTime) = stimulateOn(lastStimulate, stimulator, stimStart)
					if stimTime > protStimOn :
						tempStimulate = False
						(stimStart, stimTime, stimEnd, offTime) = stimulateOff(lastStimulate, stimulator, stimEnd)

				stimulate = tempStimulate
			
			else:
				speed = 0
				firstLine = True
				stimulate = False
				(stimStart, stimTime, stimEnd, offTime) = stimulateOff(lastStimulate, stimulator, stimEnd)
				# stimulateOff()

			if stimulate:
				if (int(stimTime) % TRIGGER_WAIT) == 0:
					# stimulator.trigger(1)
					print 'stim'
			# print stimulate
			# timeStamp = timeElapsed

			writeToFile(arenaPoint,timeElapsed,angle,speed,active,inactiveElapsed,inRestrainer,approachElapsed,ignoreElapsed,
						stimulate,firstLine,timeStamp)
			# print recording.data[0]
			# audioFreq, audioTime



			

			trackText = "Tracking"
			if active:
				activeText = "active"
				activeColor = GREEN
			else:
				activeText = "Inactive"
				activeColor = RED

			if inRestrainer:
				restrainerText =  "Approaching"
				restrainerColor = GREEN
				approachText = str(round(approachElapsed,5))

			else:
				restrainerText = "Ignoring"
				restrainerColor = RED
				approachText = str(round(ignoreElapsed,5))

			if stimulate:
				stimulateText =  "STIMULATE"
				stimulateColor = BLUE
			else:
				stimulateText = "DONT STIMULATE"
				stimulateColor = (255,255,0)

			elapsedText = str(round(timeElapsed,5))
			
			inactiveText = str(round(inactiveElapsed,5))
			audioColor = GREEN





		else:
			speed = -1
			stimulate = False
			(stimStart, stimTime, stimEnd, offTime) = stimulateOff(lastStimulate, stimulator, stimEnd)
			# stimulateOff()
			trackText = "Not Tracking"
			activeText = "Not Tracking"
			restrainerText = "Not Tracking"
			activeColor = WHITE
			activeColor = WHITE
			restrainerColor = WHITE
			elapsedText = "Not Tracking"
			approachText = "Not Tracking"
			inactiveText = "Not Tracking"
			stimulateText = "Not Tracking"
			stimulateColor = WHITE
			audioColor = WHITE

		audioTextai0 = str(audioFreqai0)
		audioTextai1 = str(audioFreqai1)

		PutText(displayImage, "Track Status: " , (5,15), FONT, Scalar(250,250,250))
		PutText(displayImage, trackText, (25,35), FONT, Scalar(250,250,250))
		PutText(displayImage, "Activity: " , (5,65), FONT, activeColor)
		PutText(displayImage, activeText, (25,85), FONT, activeColor)
		PutText(displayImage, "Location: " , (5,115), FONT, WHITE)
		PutText(displayImage,  str(arenaPoint), (25,135), FONT, WHITE)
		PutText(displayImage, "Restrainer Approach: " , (5,165), FONT, restrainerColor)
		PutText(displayImage, restrainerText, (25,185), FONT, restrainerColor)

		PutText(displayImage, "Time Elapsed: " , (5,255), FONT, Scalar(250,250,250))
		PutText(displayImage, elapsedText, (25,275), FONT, Scalar(250,250,250))
		if inRestrainer and liveTrack:
			PutText(displayImage, "Approach ", (5,305), FONT, GREEN)
			PutText(displayImage, "Elapsed: " , (90,305), FONT, Scalar(250,250,250))
		elif not inRestrainer and liveTrack:
			PutText(displayImage, "Ignore ", (5,305), FONT, RED)
			PutText(displayImage, "Elapsed: " , (68,305), FONT, Scalar(250,250,250))
		else:
			PutText(displayImage, "Approach Elapsed: ", (5,305), FONT, WHITE)
		PutText(displayImage, approachText, (25,325), FONT, restrainerColor)
		PutText(displayImage, "Inactive Elapsed: " , (5,355), FONT, Scalar(250,250,250))
		PutText(displayImage, inactiveText, (25,375), FONT, Scalar(250,250,250))
		PutText(displayImage, "Stimulator Status: ", (5, 405), FONT, WHITE)
		PutText(displayImage, stimulateText, (25,425), FONT, stimulateColor)
		PutText(displayImage, "Audio Signal ai0: ", (5, 455), FONT, WHITE)
		PutText(displayImage, audioTextai0, (25,475), FONT, audioColor)
		PutText(displayImage, "Audio Signal ai1: ", (5, 505), FONT, WHITE)
		PutText(displayImage, audioTextai1, (25,525), FONT, audioColor)
		if stimulate and liveTrack:
			if round(time.clock(),0) % 2 == 0:
				PutText(tempImage, "Stimulating", (nearRestrainer['top_left'][0]+13, nearRestrainer['top_left'][1]+20), FONT, (255,255,0))








		ShowImage("display",displayImage)

		Add(tempImage,canvas,canvas)
		if liveTrack:
			# tempFrame = numpy.asarray(GetMat(frame))   ############ Uncomment To write unedited Frame
			tempFrame = numpy.asarray(GetMat(canvas))    ############ Uncomment To Write Tracking Frame

			writer.write(tempFrame)

		
		ShowImage(window, canvas)



	if NUM_MICS == 0:
		recordingData = " "

	elif NUM_MICS == 1:
		recording.StopTask()
		recording.ClearTask()
		#recordingData = recording.timeStamps



		
	# recordingai1.StopTask()
	# recordingai1.ClearTask()

	return (recordingData)