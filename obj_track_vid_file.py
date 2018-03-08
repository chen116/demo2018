# # import the necessary packages
# from imutils.video import FileVideoStream
# from imutils.video import FPS
# import numpy as np
# import argparse
# import imutils
# import time
# import cv2
# # construct the argument parse and parse the arguments
# from tkinter import *

# master = Tk()
# MODES = [
#     ("400", 400),
#     ("800", 800),
#     ("1000", 1000),
#     ("done",0)
# ]

# w1 = IntVar()
# w1.set(400) # initialize
# previous_f_size = w1.get()
# for text, mode in MODES:
#     b = Radiobutton(master, text=text,variable=w1, value=mode)
#     b.pack(anchor=W)
# # start the file video stream thread and allow the buffer to
# # start to fill
# print("[INFO] starting video file thread...")
# fvs = FileVideoStream("walkcat.mp4").start()
# time.sleep(1.0)
# # start the FPS timer
# fps = FPS().start()


# # loop over frames from the video file stream
# while fvs.more():
# 	# grab the frame from the threaded video file stream, resize
# 	# it, and convert it to grayscale (while still retaining 3
# 	# channels)
# 	frame = fvs.read()
# 	frame = imutils.resize(frame, width=450)
# 	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# 	frame = np.dstack([frame, frame, frame])
# 	if w1.get()==0:
# 		break
# 	# display the size of the queue on the frame
# 	cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
# 		(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
 
# 	# show the frame and update the FPS counter
# 	cv2.imshow("Frame", frame)
# 	cv2.waitKey(1)
# 	fps.update()
# 	master.update_idletasks()
# 	master.update()

# 	# if fvs.more():
# 	# 	fvs = FileVideoStream("walkcat.mp4").start()
		


# # stop the timer and display FPS information
# fps.stop()
# print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# # do a bit of cleanup
# cv2.destroyAllWindows()
# fvs.stop()

# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils.video import FPS
from foscam import FoscamCamera
import numpy as np
import argparse
import imutils
import time
import cv2
import os
from tkinter import *
master = Tk()
w1 = Scale(master,from_=100,to=2000,orient=HORIZONTAL)
w1.set(400)
w1.pack()
mycam = FoscamCamera('65.114.169.154',88,'arittenbach','8mmhamcgt16!',daemon=False)
moveright = 0
moveleft = 0
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())
#os.system('python reset_cam.py') 
mycam.ptz_reset()
# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
#CLASSES = ["person"]
L=0.3
R=0.7
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
canpoint = 1
# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
# for vid file
# vs = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()
vs = FileVideoStream("walkcat.mp4").start()





time.sleep(2.0)
fps = FPS().start()
pointat = 0
# loop over the frames from the video stream
while True:


	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=w1.get())

	# for vid file
	frame = np.dstack([frame, frame, frame])


	# grab the frame dimensions and convert it to a blob
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)
#	print(w)
	# pass the blob through the network and obtain the detections and
	# predictions
	net.setInput(blob)
	detections = net.forward()
	#print(frame.dtype)
	# loop over the detections
	for i in np.arange(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the prediction
		confidence = detections[0, 0, i, 2]
		idx2 = int(detections[0,0,i,1])
		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
		if ((confidence > args["confidence"]) and (CLASSES[idx2]=='person')):
			# extract the index of the class label from the
			# `detections`, then compute the (x, y)-coordinates of
			# the bounding box for the object
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")
		#	print('startX=',startX)
		#	print('endX=',endX)
			if(((startX+endX)/2<(L*w)) and (moveleft==0)):
				mycam.ptz_move_left()
				moveleft = 1
				moveright = 0
			#	canpoint = 0
			#	pointat = time.time()+0.3 
			elif(((startX+endX)/2>(R*w)) and (moveright==0)):
				mycam.ptz_move_right()
				moveright = 1
				moveleft = 0
			#	canpoint = 0
			#	pointat = time.time()+0.3
			# draw the prediction on the frame
			elif((((startX+endX)/2>(L*w)) and (((startX+endX)/2)<(R*w))))and((moveright==1)or(moveleft==1)):
				mycam.ptz_stop_run()
				moveright = 0
				moveleft = 0
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()
	master.update_idletasks()
	master.update()
	#if(time.time()>pointat):
	#	canpoint = 1

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
