# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from foscam_v2 import FoscamCamera
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import socket
import sys
import threading

from tkinter import *
def start_server():
	global remotetrack
	remotetrack = 0
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	host = socket.gethostname()
	s.bind((host,int(sys.argv[6])))
	s.listen(5)
	print('server started')
	while True:
		connection, address = s.accept()
		while True:
			data = connection.recv(64)
			if (len(data)>0):
				msg = data.decode('utf-8')
				if (msg == 'found_object'):
					print('remote node found object')
					remotetrack = 1
				elif (msg=='lost_object'):
					print('remote node lost object')
					remotetrack = 0
			if not data:
				break
			connection.sendall(data)
		connection.close()


master = Tk()
checked = IntVar(value=0)
previous_checked = checked.get()
c = Checkbutton(master, text="anchors", variable=checked)
c.pack(side=LEFT)
FSIZE = [
    ("300", 300),
    ("600", 600),
    ("800", 800),
    ("done",0)
]
w1 = IntVar()
w1.set(300) # initialize
previous_f_size = w1.get()
for text, mode in FSIZE:
    b = Radiobutton(master, text=text,variable=w1, value=mode)
    b.pack(side=LEFT)
m1 = Scale(master,from_=1,to=15,orient=HORIZONTAL)
m1.set(5)
m1.pack(side=LEFT,fill=X)



mycam = FoscamCamera(sys.argv[1],88,sys.argv[2],sys.argv[3],daemon=False)
moveright = 0
moveleft = 0

global remotetrack
localtrack = 0
remotetrack = 0
localsearch = 0
sentfoundmessage = 0
sentlostmessage = 0
centered = 1

#sock_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#sock_client.connect((sys.argv[4],int(sys.argv[5])))
thread = threading.Thread(target = start_server)
thread.daemon = True
thread.start()
input('press enter when other node is ready')

sock_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock_client.connect((sys.argv[4],int(sys.argv[5])))

# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-p", "--prototxt", required=True,
#	help="path to Caffe 'deploy' prototxt file")
#ap.add_argument("-m", "--model", required=True,
#	help="path to Caffe pre-trained model")
#ap.add_argument("-c", "--confidence", type=float, default=0.2,
#	help="minimum probability to filter weak detections")
#args = vars(ap.parse_args())
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
prototxt = 'MobileNetSSD_deploy.prototxt.txt'
model = 'MobileNetSSD_deploy.caffemodel'
net = cv2.dnn.readNetFromCaffe(prototxt, model)
personincam = 0
# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
#vs = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()
vs = VideoStream('rtsp://'+sys.argv[2]+':'+sys.argv[3]+'@'+sys.argv[1]+':88/videoMain').start()

time.sleep(2.0)
fps = FPS().start()
pointat = 0
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=w1.get())

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
		print(detections[0,0,:,1])
		if ((confidence > 0.2) and (CLASSES[idx2]=='person')):
			# extract the index of the class label from the
			# `detections`, then compute the (x, y)-coordinates of
			# the bounding box for the object
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")
		#	print('startX=',startX)
		#	print('endX=',endX)
			if(((startX+endX)/2<(L*w))and(moveleft==0)):
				mycam.ptz_move_left()
				moveleft = 1
				moveright = 0
			#	canpoint = 0
			#	pointat = time.time()+0.3 
			elif(((startX+endX)/2>(R*w))and(moveright==0)):
				mycam.ptz_move_right()
				moveleft = 0
			#	canpoint = 0
			#	pointat = time.time()+0.3
			# draw the prediction on the frame
			elif((((startX+endX)/2>(L*w)) and (((startX+endX)/2)<(R*w))))and((moveright==1)or(moveleft==1)):
				mycam.ptz_stop_run()
				moveright = 0
				moveleft = 0
				centered = 0
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			localtrack = 1
			localsearch = 0
			sentlostmessage = 0
			centered = 0
			#sock_client.send(bytes('found_object','UTF-8'))
	myvec = detections[0,0,:,1]	
	
	if 15 in myvec:
		personincam = 1
	else:
		print('about to send lost message')
		personincam = 0
		localtrack = 0
		sock_client.send(bytes('lost_object','UTF-8'))
		sentlostmessage = 1

	if ((localsearch == 0) and (localtrack == 0) and (remotetrack == 1) and (personincam==0)):
			print('about to start cruise')
			mycam.start_horizontal_cruise()
			localsearch = 1
			localtrack = 0
			centered = 0

	if ((localtrack == 0) and (remotetrack ==0) and (centered == 0) and (personincam==0)):
			print('about to reset cam')
			mycam.ptz_reset()
			centered = 1
			localsearch = 0
			localtrack = 0
			sentfoundmessage = 0
		#elif ((confidence < 0.2) and (CLASSES[idx2]=='person') and (localsearch==0) and (remotetrack == 1) and (localtrack == 0)):
		#	print('about to start cruise')
		#	mycam.start_horizontal_cruise()
		#	localsearch = 1
		#	localtrack = 0
		#elif ((confidence < 0.2) and (CLASSES[idx2]=='person') and (localsearch==0) and (remotetrack == 0) and (centered==0)):
		#	print('about tor reset cam')
		#	mycam.ptz_reset()
		#	centered = 1
		#	localsearch = 0
		#	localtrack = 0	
		#	sock_client.send(bytes('lost_object','UTF-8'))
	# show the output frame
	cv2.imshow("Frame", frame)
	fps.update()
	master.update_idletasks()
	master.update()
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# # update the FPS counter
	# fps.update()
	# master.update_idletasks()
	# master.update()
	#if(time.time()>pointat):
	#	canpoint = 1
	print('localsearch = ',localsearch)
	print('remotetrack = ',remotetrack)
	print('localtrack = ',localtrack)
	print('personincam =',personincam)
	print('sentfoundmessage = ',sentfoundmessage)
	print('sentlostmessage = ',sentlostmessage)
	sentfoundmessage = 0
	if ((personincam==1) and (sentfoundmessage==0)):
		print('about to send found message')
		sock_client.send(bytes('found_object','UTF-8'))
		sentfoundmessage = 1

		
# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
