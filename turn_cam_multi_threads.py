# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# hb init
import heartbeat
hb = heartbeat.Heartbeat(1024,5,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode"]
comm = heartbeat.DomU(monitoring_items)






# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from foscam import FoscamCamera
import numpy as np
import argparse
import imutils
import time
import cv2
import os

from imutils.video import FileVideoStream


import threading
from queue import Queue
class Workers(threading.Thread):
	def __init__(self,threadLock,every_n_frame,thread_id,input_q,output_q):
		threading.Thread.__init__(self)
		self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
		self.thread_id=thread_id
		self.input_q=input_q
		self.output_q=output_q
		self.every_n_frame=every_n_frame
		self.threadLock=threadLock
		self.obj_track=0
	def run(self):
		# Acquire lock to synchronize thread
		# self.threadLock.acquire()
		while True:
			self.threadLock.acquire()
			self.every_n_frame['cnt']=(self.every_n_frame['cnt']+1)%5
			self.obj_track = self.every_n_frame['cnt']
			self.threadLock.release()

			blob = self.input_q.get()
			if self.obj_track%5==0:
				self.net.setInput(blob)
				self.output_q.put(self.net.forward())
			else:
				self.output_q.put(np.ndarray([0]))



		# Release lock for the next thread
		# self.threadLock.release()
		print("Exiting thread" , self.thread_id)





from tkinter import *
master = Tk()
checked = IntVar(value=0)
previous_checked = checked.get()
c = Checkbutton(master, text="anchors", variable=checked)
c.pack()

MODES = [
    ("600", 600),
    ("400", 400),
    ("600", 600),
    ("done",0)
]

w1 = IntVar()
w1.set(600) # initialize
previous_f_size = w1.get()
for text, mode in MODES:
    b = Radiobutton(master, text=text,variable=w1, value=mode)
    b.pack(anchor=W)
ml = Button(master, text="left",command= lambda: move_left(mycam))
ml.pack()
mr = Button(master,text="right",command= lambda: move_right(mycam))
mr.pack()



def move_left(mycam):
	mycam.ptz_move_left()
	mycam.ptz_stop_run()	
	print("moving lefttt")
def move_right(mycam):
	mycam.ptz_move_right()
	mycam.ptz_stop_run()	
	print("moving righttt")




mycam = FoscamCamera('65.114.169.108',88,'admin','admin',daemon=False)
moveright = 0
moveleft = 0
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
# ap.add_argument("-p", "--prototxt", required=True,
# 	help="path to Caffe 'deploy' prototxt file")
# ap.add_argument("-m", "--model", required=True,
# 	help="path to Caffe pre-trained model")
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

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
#vs = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()
vs = VideoStream('rtsp://admin:admin@65.114.169.108:88/videoMain').start()
# vs= FileVideoStream("walkcat.mp4").start()

time.sleep(2.0)

input_q = Queue()  # fps is better if queue is higher but then more lags
output_q = Queue()
threads = []
every_n_frame = {'cnt':-1}
threadLock = threading.Lock()

for i in range(3):
	tmp_thread = Workers(threadLock,every_n_frame,i,input_q,output_q)
	tmp_thread.start()
	threads.append(tmp_thread)
fps = FPS().start()
pointat = 0



prev_box = {}
# loop over the frames from the video stream
while True:
# while vs.more():
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	current_f_size=w1.get()
	if current_f_size == 0:
		break
	frame = imutils.resize(frame, width=current_f_size)


	# grab the frame dimensions and convert it to a blob
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)

	input_q.put(blob)
	if output_q.empty():
		print('empty ouput queue...')
	else:
		detections = output_q.get()
		if detections.shape[0] == 0:
			if len(prev_box)>0:
				startX=prev_box['startX']
				startY=prev_box['startY']
				endX=prev_box['endX']
				endY=prev_box['endY']
				idx=prev_box['idx']
				label=prev_box['label']
				cv2.rectangle(frame, (startX, startY), (endX, endY),
					COLORS[idx], 2)
				y = startY - 15 if startY - 15 > 15 else startY + 15
				cv2.putText(frame, label, (startX, y),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)				


		else:
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
					print('catttttttttttttttttt')
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
					prev_box['startX']=startX
					prev_box['startY']=startY
					prev_box['endX']=endX
					prev_box['endY']=endY
					prev_box['idx']=idx
					prev_box['label']=label

		# show the output frame
		cv2.imshow("Frame", frame)
		fps.update()

		key = cv2.waitKey(1) & 0xFF

		# hb stuff
		hb.heartbeat_beat()
		window_hr = hb.get_window_heartrate()
		comm.write("heart_rate",window_hr)
		print('--------------------',window_hr)
		current_checked = checked.get()
		if previous_checked!=current_checked:
			comm.write("app_mode",current_checked)
			previous_checked=current_checked


	# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
		if key == ord("l"):
			move_left(mycam)
		if key ==ord("r"):
			move_right(mycam)



	# update the FPS counter
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
for t in threads:
	t.join()
# hb clean up
hb.heartbeat_finish()
comm.write("heart_rate","done")
