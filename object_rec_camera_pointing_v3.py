# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from foscam_v3 import FoscamCamera
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import socket
import sys
import threading
import copy
from imutils.video import FileVideoStream



import threading
from queue import Queue



# setup GUI

if True:
	from tkinter import *
	master = Tk()
	w = 800#475#550 # width for the Tk root
	h = 75 # height for the Tk root
	# get screen width and height
	ws = master.winfo_screenwidth() # width of the screen
	hs = master.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs)-h*2
	# set the dimensions of the screen 
	# and where it is placed
	master.geometry('%dx%d+%d+%d' % (w, h, x, y))

	sched_var = StringVar()
	sched_var.set(" || "+sys.argv[7]+" ||")
	fg ="blue"
	if "redit" in sys.argv[7]:
		fg = "green"

	sched_label = Label(master, textvariable=sched_var,fg = fg,bg = "white",font = "Verdana 30 bold" )
	sched_label.pack(side=LEFT)

	# scheds = [
	#     ("Credit", 0),
	#     ("RT-Xen", 1)
	# ]
	# sched = IntVar()
	# sched.set(0) # initialize
	# previous_sched = sched.get()
	# for text, mode in scheds:
	#     b = Radiobutton(master, text=text,variable=sched, value=mode)
	#     b.pack(side=LEFT)

	checked = IntVar(value=0)
	previous_checked = checked.get()
	c = Checkbutton(master, text="Anchors | ", variable=checked,font = "Verdana 15" )
	c.pack(side=LEFT)


	frame_var = StringVar()
	frame_var.set("Frame Size:")
	frame_label = Label(master, textvariable=frame_var)
	frame_label.pack(side=LEFT)
	FSIZE = [
	    ("300", 300),
	    ("600", 600),
	    ("800", 800)
	]
	w1 = IntVar()
	w1.set(300) # initialize
	previous_f_size = w1.get()

	for text, mode in FSIZE:
	    b = Radiobutton(master, text=text,variable=w1, value=mode)
	    b.pack(side=LEFT)

	def exit_app(w1):
		w1.set(0)
	done = Button(master, text="EXIT",command=lambda: exit_app(w1),font = "Verdana 10" )
	done.pack(side=LEFT)


	# anchors_var = StringVar()
	# anchors_var.set("Meow")
	# anchors_label = Label(master, textvariable=anchors_var)
	# anchors_label.pack(side=BOTTOM)



	m1 = Scale(master,from_=1,to=20,orient=HORIZONTAL)
	m1.set(5) # init speed
	# m1.pack(side=LEFT)




class Workers(threading.Thread):
	def __init__(self,threadLock,every_n_frame,thread_id,input_q,output_q):
		threading.Thread.__init__(self)
		self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
		self.thread_id=thread_id
		self.input_q=input_q
		self.output_q=output_q
		self.every_n_frame=every_n_frame
		self.n=every_n_frame['n']
		self.threadLock=threadLock
		self.my_every_n_frame_cnt=0
	def run(self):
		# Acquire lock to synchronize thread
		# self.threadLock.acquire()
		while True:

			self.threadLock.acquire()
			self.n = self.every_n_frame['n']
			# self.every_n_frame['cnt']=(self.every_n_frame['cnt']+1)%self.n
			# self.my_every_n_frame_cnt = self.every_n_frame['cnt']
			self.threadLock.release()
			if self.n==-1:
				# self.output_q.put({'cnt':-1})
				break
			# blob = self.input_q.get()
			stuff = self.input_q.get()
			if stuff['cnt']==-1:
				self.output_q.put({'cnt':-1})
				break
			# self.n = stuff['n']
			self.my_every_n_frame_cnt = stuff['cnt']

			blob = stuff['blob']
			if self.my_every_n_frame_cnt%self.n==0:
				self.net.setInput(blob)
				#print("--------------------thread:",self.thread_id," gonna dnn", "cnt:",self.my_every_n_frame_cnt,'n:',self.n)
				# self.output_q.put(self.net.forward())
				# self.output_q.put({'blob':self.net.forward(),'cnt':stuff['cnt']})
				net_result=self.net.forward()
				# self.output_q.put({'blob':net_result,'cnt':stuff['cnt']})
				self.output_q.put({'blob':net_result,'cnt':stuff['cnt']})

			else:
				# self.output_q.put({'blob':-1*np.ones((1,1,1,2)),'cnt':stuff['cnt']})
				self.output_q.put({'blob':-1*np.ones((1,1,1,2)),'cnt':stuff['cnt']})
				# self.output_q.put(np.ndarray([0]))



		# Release lock for the next thread
		# self.threadLock.release()
		#print("Exiting thread" , self.thread_id)
input_q = Queue()  # fps is better if queue is higher but then more lags
output_q = Queue()

threads = []
every_n_frame = {'cnt':-1,'n':m1.get()}
threadLock = threading.Lock()
total_num_threads = 5
num_threads_exiting = 0

def start_server():
	global remotetrack
	remotetrack = 0
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	host = socket.gethostname()
	s.bind((host,int(sys.argv[6])))
	s.listen(5)
	#print('server started')
	while True:
		connection, address = s.accept()
		while True:
			data = connection.recv(64)
			if (len(data)>0):
				msg = data.decode('utf-8')
				if (msg == 'found_object'):
					#print('remote node found object')
					remotetrack = 1
				elif (msg=='lost_object'):
					#print('remote node lost object')
					remotetrack = 0
				elif (msg=='clean_up'):
					#print('cleanup from other node')
					remotetrack = -1
			if not data:
				break
			connection.sendall(data)
		remotetrack = -1
		connection.close()
	remotetrack = -1




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


sock_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tempFlag=None
while tempFlag is None:
	try:
		sock_client.connect((sys.argv[4],int(sys.argv[5])))
		tempFlag=1
	except:
		#print("Waiting for other host")
		time.sleep(1)
		pass

#setup CAM
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
# #print("[INFO] loading model...")
# prototxt = 'MobileNetSSD_deploy.prototxt.txt'
# model = 'MobileNetSSD_deploy.caffemodel'
# net = cv2.dnn.readNetFromCaffe(prototxt, model)
personincam = 0
# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
#print("[INFO] starting video stream...")
#vs = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()
vs = VideoStream('rtsp://'+sys.argv[2]+':'+sys.argv[3]+'@'+sys.argv[1]+':88/videoMain').start() # realvid
# vs= FileVideoStream("walkcat.mp4").start() # outvid



tracking_target = "person" # realvid
# tracking_target = "cat"  # outvid



time.sleep(2.0)

# cat_frame = vs.read()  # outvid
# for x in range(10):  # outvid
# 	cat_frame = vs.read()  # outvid


# setup mulithreads

for i in range(total_num_threads):
	tmp_thread = Workers(threadLock,every_n_frame,i,input_q,output_q)
	tmp_thread.start()
	threads.append(tmp_thread)
# prev_box = {}
prev_boxes = []
# loop over the frames from the video stream
cnt=0
global_cnt=0

import heartbeat
window_size_hr=5
hb = heartbeat.Heartbeat(1024,window_size_hr,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode","frame_size"]
comm = heartbeat.DomU(monitoring_items)
fps = FPS().start()
pointat = 0
# loop over the frames from the video stream

prev_personincam = personincam
# while vs.more(): # outvid
while True: # realvid

	frame = vs.read()
	if True:#frame is not None:
		# frame = cat_frame # outvid
		current_f_size=w1.get()
		if remotetrack == -1 or current_f_size == 0:
			threadLock.acquire()
			every_n_frame['n']=-1
			threadLock.release()
			while not input_q.empty():
				x=input_q.get()		
			for i in range(total_num_threads):
				input_q.put({'cnt':-1})
			break		

		if current_f_size > 0:
			frame = imutils.resize(frame, width=current_f_size)
			# grab the frame dimensions and convert it to a blob
			(h, w) = frame.shape[:2]
			blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
				0.007843, (300, 300), 127.5)
			threadLock.acquire()
			every_n_frame['n']=m1.get()
			threadLock.release()
			stuff={'blob':blob,'cnt':cnt,'n':m1.get()}
			cnt+=1
			input_q.put(stuff)
			# stuff={'blob':blob,'cnt':cnt,'n':m1.get()}
			# cnt+=1
			# input_q.put(stuff)

		# if not output_q.empty():
		# 	stuff = output_q.get()
		# 	detections = stuff['blob']
		# 	order = stuff['cnt']
		# 	#print('output cnt:',order,'global cnt:',global_cnt)
		# 	global_cnt+=1

		# 	if detections[0][0][0][0] == -1:
		# 		if len(prev_boxes)>0:
		# 			for prev_box in prev_boxes:
		# 				startX=prev_box['startX']
		# 				startY=prev_box['startY']
		# 				endX=prev_box['endX']
		# 				endY=prev_box['endY']
		# 				idx=prev_box['idx']
		# 				label=prev_box['label']
		# 				cv2.rectangle(frame, (startX, startY), (endX, endY),
		# 					COLORS[idx], 2)
		# 				y = startY - 15 if startY - 15 > 15 else startY + 15
		# 				cv2.putText(frame, label, (startX, y),
		# 					cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)					
		# 	else:
		# 		prev_boxes=[]
		# 		for i in np.arange(0, detections.shape[2]):
		# 			# extract the confidence (i.e., probability) associated with
		# 			# the prediction
		# 			confidence = detections[0, 0, i, 2]
		# 			idx2 = int(detections[0,0,i,1])
		# 			# filter out weak detections by ensuring the `confidence` is
		# 			# greater than the minimum confidence
		# 			if ((confidence > 0.2) and (CLASSES[idx2]==tracking_target)):
		# 				# extract the index of the class label from the
		# 				# `detections`, then compute the (x, y)-coordinates of
		# 				# the bounding box for the object
		# 				# #print('catttttttttttttttttt')
		# 				idx = int(detections[0, 0, i, 1])
		# 				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		# 				(startX, startY, endX, endY) = box.astype("int")
		# 			#	#print('startX=',startX)
		# 			#	#print('endX=',endX)
		# 				if(((startX+endX)/2<(L*w)) and (moveleft==0)):
		# 					mycam.ptz_move_left()
		# 					moveleft = 1
		# 					moveright = 0
		# 				#	canpoint = 0
		# 				#	pointat = time.time()+0.3 
		# 				elif(((startX+endX)/2>(R*w)) and (moveright==0)):
		# 					mycam.ptz_move_right()
		# 					moveright = 1
		# 					moveleft = 0
		# 				#	canpoint = 0
		# 				#	pointat = time.time()+0.3
		# 				# draw the prediction on the frame
		# 				elif((((startX+endX)/2>(L*w)) and (((startX+endX)/2)<(R*w))))and((moveright==1)or(moveleft==1)):
		# 					mycam.ptz_stop_run()
		# 					moveright = 0
		# 					moveleft = 0
		# 				label = "{}: {:.2f}%".format(CLASSES[idx],
		# 					confidence * 100)
		# 				cv2.rectangle(frame, (startX, startY), (endX, endY),
		# 					COLORS[idx], 2)
		# 				y = startY - 15 if startY - 15 > 15 else startY + 15
		# 				cv2.putText(frame, label, (startX, y),
		# 					cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
		# 				prev_box = {}
		# 				prev_box['startX']=startX
		# 				prev_box['startY']=startY
		# 				prev_box['endX']=endX
		# 				prev_box['endY']=endY
		# 				prev_box['idx']=idx
		# 				prev_box['label']= "recalculating..."
		# 				prev_boxes.append(prev_box)
		# 				localtrack = 1
		# 				localsearch = 0
		# 				sentlostmessage = 0
		# 				centered = 0

		# 	#elif ((confidence < 0.2) and (CLASSES[idx2]=='person') and (localsearch==0) and (remotetrack == 1) and (localtrack == 0)):
		# 		#	#print('about to start cruise')
		# 		#	mycam.start_horizontal_cruise()
		# 		#	localsearch = 1
		# 		#	localtrack = 0
		# 		#elif ((confidence < 0.2) and (CLASSES[idx2]=='person') and (localsearch==0) and (remotetrack == 0) and (centered==0)):
		# 		#	#print('about tor reset cam')
		# 		#	mycam.ptz_reset()
		# 		#	centered = 1
		# 		#	localsearch = 0
		# 		#	localtrack = 0	
		# 		#	sock_client.send(bytes('lost_object','UTF-8'))
		# 	# show the output frame
		# 	cv2.imshow("Frame", frame)
		# 	# hb stuff
		# 	# #print("hb: before heartbeat_beat()")
		# 	hb.heartbeat_beat()
		# 	# #print("hb: before get_window_heartrate()")
		# 	window_hr = hb.get_window_heartrate()
		# 	# #print("hb: before get_instant_heartrate()")
		# 	# instant_hr = hb.get_instant_heartrate()
		# 	# #print("hb: after hb stuff")
		# 	if global_cnt>window_size_hr:
		# 		comm.write("heart_rate",window_hr)
		# 	# #print('------------------window_hr:',window_hr)
		# 	# #print('instant_hr:',instant_hr)
		# 	current_checked = checked.get()
		# 	if previous_checked!=current_checked:
		# 		comm.write("app_mode",current_checked)
		# 		previous_checked=current_checked
		# 	if previous_f_size!=current_f_size:
		# 		comm.write("frame_size",current_f_size)
		# 		previous_f_size=current_f_size

		if not output_q.empty():
			stuff = output_q.get()
			detections = stuff['blob']
			order = stuff['cnt']
			#print('output cnt:',order,'global cnt:',global_cnt)
			global_cnt+=1

			if detections[0][0][0][0] == -1:
				if len(prev_boxes)>0:
					for prev_box in prev_boxes:
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
				prev_boxes=[]
				for i in np.arange(0, detections.shape[2]):
					# extract the confidence (i.e., probability) associated with
					# the prediction
					confidence = detections[0, 0, i, 2]
					idx2 = int(detections[0,0,i,1])
					# filter out weak detections by ensuring the `confidence` is
					# greater than the minimum confidence
					if ((confidence > 0.2) and (CLASSES[idx2]==tracking_target)):
						# extract the index of the class label from the
						# `detections`, then compute the (x, y)-coordinates of
						# the bounding box for the object
						# #print('catttttttttttttttttt')
						idx = int(detections[0, 0, i, 1])
						box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
						(startX, startY, endX, endY) = box.astype("int")
					#	#print('startX=',startX)
					#	#print('endX=',endX)
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
						prev_box = {}
						prev_box['startX']=startX
						prev_box['startY']=startY
						prev_box['endX']=endX
						prev_box['endY']=endY
						prev_box['idx']=idx
						prev_box['label']= "recalculating..."
						prev_boxes.append(prev_box)
						localtrack = 1
						localsearch = 0
						sentlostmessage = 0
						centered = 0

			myvec = detections[0,0,:,1]	
			

			if myvec[0]!=-1:
				if CLASSES.index(tracking_target) in myvec:
					personincam = 1
					prev_personincam=1
				else:
					#print('about to send lost message')
					personincam = 0
					prev_personincam = 0
					localtrack = 0
					sock_client.send(bytes('lost_object','UTF-8'))
					sentlostmessage = 1
			else:
				personincam = prev_personincam
				if personincam == 0:
					#print('about to send lost message')
					personincam = 0
					prev_personincam = 0
					localtrack = 0
					sock_client.send(bytes('lost_object','UTF-8'))
					sentlostmessage = 1

			if ((localsearch == 0) and (localtrack == 0) and (remotetrack == 1) and (personincam==0)):
					#print('about to start cruise')
					mycam.start_cruise('mycruise')
					localsearch = 1
					localtrack = 0
					centered = 0

			if ((localtrack == 0) and (remotetrack ==0) and (centered == 0) and (personincam==0)):
					#print('about to reset cam')
					mycam.ptz_reset()
					centered = 1
					localsearch = 0
					localtrack = 0
					sentfoundmessage = 0
				#elif ((confidence < 0.2) and (CLASSES[idx2]=='person') and (localsearch==0) and (remotetrack == 1) and (localtrack == 0)):
				#	#print('about to start cruise')
				#	mycam.start_horizontal_cruise()
				#	localsearch = 1
				#	localtrack = 0
				#elif ((confidence < 0.2) and (CLASSES[idx2]=='person') and (localsearch==0) and (remotetrack == 0) and (centered==0)):
				#	#print('about tor reset cam')
				#	mycam.ptz_reset()
				#	centered = 1
				#	localsearch = 0
				#	localtrack = 0	
				#	sock_client.send(bytes('lost_object','UTF-8'))
			# show the output frame
			cv2.imshow("Frame", frame)
			# hb stuff
			# #print("hb: before heartbeat_beat()")
			hb.heartbeat_beat()
			# #print("hb: before get_window_heartrate()")
			window_hr = hb.get_window_heartrate()
			# #print("hb: before get_instant_heartrate()")
			# instant_hr = hb.get_instant_heartrate()
			# #print("hb: after hb stuff")
			if global_cnt>window_size_hr:
				comm.write("heart_rate",window_hr)
			# #print('------------------window_hr:',window_hr)
			# #print('instant_hr:',instant_hr)
			current_checked = checked.get()
			if previous_checked!=current_checked:
				comm.write("app_mode",current_checked)
				previous_checked=current_checked
			if previous_f_size!=current_f_size:
				comm.write("frame_size",current_f_size)
				previous_f_size=current_f_size
			# current_sched = sched.get()
			# if previous_sched!=current_sched:
			# 	comm.write("sched",current_sched)
			# 	previous_sched=current_sched
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
			#print('localsearch = ',localsearch)
			#print('remotetrack = ',remotetrack)
			#print('localtrack = ',localtrack)
			#print('personincam =',personincam)
			#print('sentfoundmessage = ',sentfoundmessage)
			#print('sentlostmessage = ',sentlostmessage)
			sentfoundmessage = 0
			if ((personincam==1) and (sentfoundmessage==0)):
				#print('about to send found message')
				sock_client.send(bytes('found_object','UTF-8'))
				sentfoundmessage = 1
			
# stop the timer and display FPS information
fps.stop()
#print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
#print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

# hb clean up
hb.heartbeat_finish()
comm.write("heart_rate","done")

# worker threads clean up
threadLock.acquire()
every_n_frame['n']=-1 
threadLock.release()
while not input_q.empty(): 
	x=input_q.get()	 
for i in range(total_num_threads): 
	input_q.put({'cnt':-1})
for t in threads:
	t.join()
#print("worker threads cleaned up")
# mycam1 = FoscamCamera('65.114.169.154',88,'arittenbach','8mmhamcgt16!')
# mycam2 = FoscamCamera('65.114.169.108',88,'admin','admin')
mycam1 = FoscamCamera('65.114.169.139',88,'arittenbach','8mmhamcgt16!')
mycam2 = FoscamCamera('65.114.169.151',88,'admin','admin')

mycam1.ptz_reset()
mycam2.ptz_reset()
mycam1.set_ptz_speed(4)
mycam2.set_ptz_speed(4)
if remotetrack!=-1:
	sock_client.send(bytes('clean_up','UTF-8'))
