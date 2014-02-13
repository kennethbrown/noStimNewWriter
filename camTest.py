import cv2.cv as cv
from cv import *
import time
import numpy as np
import time


#cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
#capture = cv.CaptureFromCAM(0)

# def repeat():
    # frame = cv.QueryFrame(capture)
    # cv.ShowImage("w1", frame)

# while True:
    #repeat()
    # if cv.WaitKey(33)==27:
        # break
				

cv.NamedWindow("camImg", cv.CV_WINDOW_AUTOSIZE)
capture = cv.CaptureFromCAM(0)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FORMAT, cv.IPL_DEPTH_8U)
def repeat():
	frame = cv.QueryFrame(capture)
	if frame:
		size = getSize(frame)
		print size
	cv.ShowImage("camImg", frame)
	
while True:
	repeat()
	if cv.WaitKey(33)==27:
		break
		

