# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

import heartbeat
hb = heartbeat.Heartbeat(1024,10,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode"]
comm = heartbeat.DomU(monitoring_items)



# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
from tkinter import *
# master = Tk()
# w1 = Scale(master,from_=400,to=2000,orient=HORIZONTAL)
# w1.set(400)
# w1.pack()


master = Tk()


checked = IntVar(value=0)
previous_checked = checked.get()


c = Checkbutton(master, text="anchors", variable=checked)
c.pack()

MODES = [
    ("200", 200),
    ("850", 850),
    ("1000", 1000),
    ("done",0)
]

w1 = IntVar()
w1.set(200) # initialize
previous_f_size = w1.get()
for text, mode in MODES:
    b = Radiobutton(master, text=text,variable=w1, value=mode)
    b.pack(anchor=W)
# while v.get()!=2000:
# 	x=input('->')
# 	print(v.get())
# 	master.update_idletasks()
# 	master.update()


# exit()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
#ap.add_argument("-p", "--prototxt", required=True,
#	help="path to Caffe 'deploy' prototxt file")
#ap.add_argument("-m", "--model", required=True,
#	help="path to Caffe pre-trained model")
#ap.add_argument("-c", "--confidence", type=float, default=0.2,
#	help="minimum probability to filter weak detections")
#args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
#CLASSES = ["person"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
#net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
vs = VideoStream('rtsp://admin:admin@65.114.169.108:88/videoMain').start()

# vs = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()
time.sleep(2.0)
fps = FPS().start()

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	current_f_size=w1.get()
	if current_f_size == 0:
		break
	frame = imutils.resize(frame, width=current_f_size)

	# grab the frame dimensions and convert it to a blob
#	(h, w) = frame.shape[:2]
#	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
#		0.007843, (300, 300), 127.5)

	# pass the blob through the network and obtain the detections and
	# predictions
#	net.setInput(blob)
#	detections = net.forward()
	#print(frame.dtype)
	# loop over the detections
#	for i in np.arange(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the prediction
#		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
#		if confidence > args["confidence"]:
			# extract the index of the class label from the
			# `detections`, then compute the (x, y)-coordinates of
			# the bounding box for the object
#			idx = int(detections[0, 0, i, 1])
#			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#			(startX, startY, endX, endY) = box.astype("int")

			# draw the prediction on the frame
#			label = "{}: {:.2f}%".format(CLASSES[idx],
#				confidence * 100)
#			cv2.rectangle(frame, (startX, startY), (endX, endY),
#				COLORS[idx], 2)
#			y = startY - 15 if startY - 15 > 15 else startY + 15
#			cv2.putText(frame, label, (startX, y),
#				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

	# show the output frame
	cv2.imshow("Frame", frame)
	hb.heartbeat_beat()
	window_hr = hb.get_window_heartrate()
	comm.write("heart_rate",window_hr)

	current_checked = checked.get()
	if previous_checked!=current_checked:
		comm.write("app_mode",current_checked)
		previous_checked=current_checked


	# if (current_f_size!=previous_f_size):
	# 	comm.write("app_mode",int(current_f_size/500))
	# 	previous_f_size=current_f_size
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()
	master.update_idletasks()
	master.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
hb.heartbeat_finish()
comm.write("heart_rate","done")