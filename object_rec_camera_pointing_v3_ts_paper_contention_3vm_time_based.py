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
	w = 1000 # width for the Tk root
	h = 50 # height for the Tk root
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
	fg ="green"
	if "RT" in sys.argv[7]:
		fg = "blue"

	sched_label = Label(master, textvariable=sched_var,fg = fg,bg = "white",font = "Verdana 20 bold" )
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

	# checked = IntVar(value=0)
	# previous_checked = checked.get()
	# c = Checkbutton(master, text="Anchors | ", variable=checked,font = "Verdana 14 bold" )
	# c.pack(side=LEFT)


	anchors_var = StringVar()
	anchors_var.set("Resource:")
	anchors_label = Label(master, textvariable=anchors_var,font = "Verdana 10 bold" )
	anchors_label.pack(side=LEFT)
	anchors_options = [
	    ("simple", 1),
	    ("50%",0),
	    ("100%", 2),
	    ("aimd", 4),
	    ("apid", 3)
	]
	checked = IntVar()
	checked.set(0) # initialize
	previous_checked = checked.get()

	for text, mode in anchors_options:
	    b = Radiobutton(master, text=text,variable=checked, value=mode)
	    b.pack(side=LEFT)


	frame_var = StringVar()
	frame_var.set("Freq:")
	frame_label = Label(master, textvariable=frame_var,font = "Verdana 10 bold" )
	frame_label.pack(side=LEFT)
	FSIZE = [
	    ("L", 9),
	    ("M", 6),
	    ("H", 3)
	]
	w1 = IntVar()
	w1.set(FSIZE[0][1]) # initialize
	previous_freq = w1.get()
	window_size_hr=18
	for text, mode in FSIZE:
	    b = Radiobutton(master, text=text,variable=w1, value=mode)
	    b.pack(side=LEFT)

	timeslice_var = StringVar()
	timeslice_var.set(" | ")
	timeslice_label = Label(master, textvariable=timeslice_var,font = "Verdana 10 bold" )
	timeslice_label.pack(side=LEFT)
	tsSIZE = [
	    ("Low-lat", 15),
	    ("High-thru", 30)
	]
	ts1 = IntVar()
	ts1.set(15) # initialize
	previous_ts = ts1.get()
	for text, mode in tsSIZE:
	    b = Radiobutton(master, text=text,variable=ts1, value=mode)
	    b.pack(side=LEFT)


	# ts1 = Scale(master,from_=15,to=30,orient=HORIZONTAL)
	# ts1.set(15) # init speed
	# previous_ts = ts1.get()
	# ts1.pack(side=LEFT)


	def exit_app(w1):
		w1.set(0)
	done = Button(master, text="EXIT",command=lambda: exit_app(w1))
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



			stuff = self.input_q.get()

			if stuff['cnt']==-1:
				self.output_q.put({'cnt':-1})
				break
			# self.n = stuff['n']ß
			self.my_every_n_frame_cnt = stuff['cnt']

			blob = stuff['blob']
			if self.my_every_n_frame_cnt%self.n==0:
				self.net.setInput(blob)


				net_result=self.net.forward()
				self.output_q.put({'blob':net_result,'cnt':stuff['cnt']})
				# self.output_q.put({'blob':-1*np.ones((1,1,1,2)),'cnt':stuff['cnt']})


			else:

				self.output_q.put({'blob':-1*np.ones((1,1,1,2)),'cnt':stuff['cnt']})
			# try:
			# 	stuff = self.input_q.get()

			# 	if stuff['cnt']==-1:
			# 		self.output_q.put({'cnt':-1})
			# 		break
			# 	# self.n = stuff['n']
			# 	self.my_every_n_frame_cnt = stuff['cnt']
			# 	net_result=-1*np.ones((1,1,1,2))
			# 	if self.my_every_n_frame_cnt%self.n==0:
			# 		blob = stuff['blob']
			# 		self.net.setInput(blob)
			# 		net_result=self.net.forward()
			# 	try:
			# 		self.output_q.put({'blob':net_result,'cnt':stuff['cnt']})
			# 	except:
			# 		print(thread_id,"thread not gonna wait put")
			# except:
			# 	print(thread_id,"thread not gonna wait get")



input_q = Queue()  # fps is better if queue is higher but then more lags
output_q = Queue()

m1 = IntVar()
m1.set(5)
threads = []
every_n_frame = {'cnt':-1,'n':w1.get()}
threadLock = threading.Lock()
# total_num_threads = 3 # realvid
total_num_threads = 4 # fastcat
num_threads_exiting = 0


def start_server():
	global remotetrack
	remotetrack = 0
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	host = socket.gethostname()
	tempFlag = None


	s.bind((host,int(sys.argv[6])))

	s.listen(5)
	#print('server started')
	while True:
		connection, address = s.accept()
		while True:
			data = connection.recv(64)
			if (len(data)>0):
				msg = data.decode('utf-8')
				if (msg == 'H'):
					#print('remote node found object')
					remotetrack = FSIZE[2][1]
				elif (msg=='M'):
					#print('remote node lost object')
					remotetrack = FSIZE[1][1]
				elif (msg=='L'):
					#print('remote node lost object')
					remotetrack = FSIZE[0][1]
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

synch = 0
# synch = 1 #synch
if synch:
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


# tracking_target = "person" # realvid
tracking_target = ["cat","person","car"]  # outvid # fastcat
# vs = VideoStream('rtsp://'+sys.argv[2]+':'+sys.argv[3]+'@'+sys.argv[1]+':88/videoMain').start() # realvid
# vs= FileVideoStream("walkcat.mp4").start() # outvid
# time.sleep(2.0) # realvid
catlen=0
catlen=1 # fastcat
manlen=1
carlen=1
onecatvidlen = 1
onemanvidlen = 1
onecarvidlen = 1
vidarray = None
print('video setting up')

if catlen>0: 

	#fps = FPS().start()
	x = 0
	# loop over the frames from the video stream
	cat_vidarray = np.zeros((onecatvidlen*catlen,360,640,3),dtype=np.uint8)
	vs= FileVideoStream("walkcat.mp4").start()
	time.sleep(2.0)
	for a in range(onecatvidlen):
		frame = vs.read()
		for i in range(catlen):
			cat_vidarray[a+(i*onecatvidlen),:,:,:]=frame
	vs.stop()
	print('meow')

	man_vidarray = np.zeros((onemanvidlen*manlen,360,640,3),dtype=np.uint8)
	vs= FileVideoStream("walkman.mp4").start()
	time.sleep(2.0)
	for a in range(onemanvidlen):
		frame = vs.read()
		for i in range(manlen):
			man_vidarray[a+(i*onemanvidlen),:,:,:]=frame
	vs.stop()	
	print('hi')



	# car_vidarray = np.zeros((onecarvidlen*carlen,360,640,3),dtype=np.uint8)
	# vs= FileVideoStream("walkcar.mp4").start()
	# time.sleep(2.0)
	# for a in range(onecarvidlen):
	# 	frame = vs.read()
	# 	for i in range(carlen):
	# 		car_vidarray[a+(i*onecarvidlen),:,:,:]=frame
	# vs.stop()
	# print('vroom')


	cat, man = cat_vidarray,man_vidarray

	# if "RT" in sys.argv[7]:

	# 	# vidarray = np.concatenate((car_vidarray[0:len(car_vidarray/2)],car_vidarray,cat_vidarray,cat_vidarray,man_vidarray,car_vidarray),axis=0)

	# 	# vidarray=[]
	# 	# for i in range(550):
	# 	# 	vidarray.append(cat)
	# 	# for i in range(549,782):
	# 	# 	vidarray.append(man)
	# 	# for i in range(781,988):
	# 	# 	vidarray.append(cat)
	# 	# for i in range(987,1062):
	# 	# 	vidarray.append(man)
	# 	# for i in range(1061,1200):
	# 	# 	vidarray.append(cat)


	# 	vidarray = []
	# 	for i in range(10):
	# 		vidarray.append(cat)
	# 	while len(vidarray)<=1200:
	# 		waittime4man = int(np.random.exponential(800,1))
	# 		print('waittime4man',waittime4man)
	# 		while waittime4man>0:
	# 			vidarray.append(cat)
	# 			if len(vidarray)>=1200:
	# 				break
	# 			waittime4man-=1
	# 		if len(vidarray)>=1200:
	# 			break
	# 		hangtime4man = int(np.random.exponential(800/2,1))
	# 		print('hangtime4man',hangtime4man)

	# 		while hangtime4man>0:
	# 			vidarray.append(man)
	# 			if len(vidarray)>=1200:
	# 				break
	# 			hangtime4man-=1






	# else:
	# 	# vidarray = np.concatenate((car_vidarray,cat_vidarray,man_vidarray,man_vidarray,car_vidarray,car_vidarray[0:len(car_vidarray/2)]),axis=0)
		
	# 	vidarray=[]
	# 	for i in range(900):
	# 		vidarray.append(cat)
	# 	for i in range(899,1004):
	# 		vidarray.append(man)
	# 	for i in range(1003,1200):
	# 		vidarray.append(cat)


	# vidarray=np.concatenate( vidarray, axis=0 )
	# print(len(vidarray))


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
output_q_cnt=-1

import heartbeat

hb = heartbeat.Heartbeat(1024,window_size_hr,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode","frame_size","timeslice"]
comm = heartbeat.DomU(monitoring_items)
# fps = FPS().start()
pointat = 0
# loop over the frames from the video stream

prev_personincam = personincam


# while vs.more(): # outvid
# while True:
# for frame in vidarray: # fastcat
# while True: # realvid
time_start= time.time()
while time.time()-time_start<120: # realvid

	# frame = vs.read() # realvid
	# frame = cat_frame # outvid
	frame=None
	time_cur = time.time()
	if "RT" in sys.argv[7]:
		if time_cur-time_start <30:
			frame=cat[0]
		elif time_cur-time_start <60:
			frame=cat[0]
		elif time_cur-time_start <90:
			frame=man[0]
		else:
			frame=man[0]

	else:
		if time_cur-time_start <30:
			frame=cat[0]
		elif time_cur-time_start <60:
			frame=man[0]
		elif time_cur-time_start <90:
			frame=man[0]
		else:
			frame=cat[0]	


	run_threads = 1
	if run_threads==0:
		if True:
			cnt+=1
			print(cnt)
			frame = imutils.resize(frame, width=300)
			cv2.imshow("Frame", frame)
			# hb stuff
			hb.heartbeat_beat()
			output_q_cnt=10

			if output_q_cnt>window_size_hr:
				comm.write("heart_rate",hb.get_instant_heartrate())		
			# fps.update()
			master.update_idletasks()
			master.update()
		else:
			cnt+=1
			print(cnt)

			time.sleep(1)
			hb.heartbeat_beat()
			output_q_cnt=10


			if output_q_cnt>window_size_hr:
				comm.write("heart_rate",hb.get_instant_heartrate())	

	if run_threads==1 and frame is not None:


		current_freq=w1.get()
		if remotetrack == -1 or w1.get() == 0:
			threadLock.acquire()
			every_n_frame['n']=-1
			threadLock.release()
			while not input_q.empty():
				x=input_q.get()		
			for i in range(total_num_threads):
				input_q.put({'cnt':-1})
			break		
		# current_frame_size=400 # realvid
		current_frame_size=600 # fastcat
		if current_frame_size > 0:
			frame = imutils.resize(frame, width=current_frame_size)
			# grab the frame dimensions and convert it to a blob
			(h, w) = frame.shape[:2]
			blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
				0.007843, (300, 300), 127.5)
			threadLock.acquire()
			every_n_frame['n']=w1.get()
			threadLock.release()
			stuff={'blob':blob,'cnt':cnt,'n':w1.get()}
			cnt+=1
			input_q.put(stuff)
			# try:
			# 	input_q.put_nowait(stuff)
			# except:
			# 	print("main not gonna wait put")
			


		if True:#not output_q.empty():
			object_detected = ''
			stuff = output_q.get()
			# stuff=None
			# try:
			# 	stuff = output_q.get_nowait()
			# except:
			# 	print("main not gonna wait get")
			# 	stuff = {'blob':-1*np.ones((1,1,1,2)),'cnt':output_q_cnt}


			# stuff = output_q.get()
			detections = stuff['blob']
			order = stuff['cnt']
			#print('output cnt:',order,'global cnt:',output_q_cnt)
			output_q_cnt+=1

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
					if ((confidence > 0.2) and (CLASSES[idx2] in tracking_target)):
						object_detected = CLASSES[idx2]
						# extract the index of the class label from the
						# `detections`, then compute the (x, y)-coordinates of
						# the bounding box for the object
						# #print('catttttttttttttttttt')
						idx = int(detections[0, 0, i, 1])
						box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
						(startX, startY, endX, endY) = box.astype("int")
					#	#print('startX=',startX)
					#	#print('endX=',endX)

						# label =str(order)+'--'
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
						prev_box['label']= label
						prev_boxes.append(prev_box)
						localtrack = 1
						localsearch = 0
						sentlostmessage = 0
						centered = 0

			myvec = detections[0,0,:,1]	
			


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
			# comm.write("heart_rate",hb.get_instant_heartrate())

			if output_q_cnt>window_size_hr and output_q_cnt%w1.get()==0:
				comm.write("heart_rate",hb.get_window_heartrate())
			current_app_mode = checked.get()
			if previous_checked!=current_app_mode and output_q_cnt%w1.get()==0:
				comm.write("app_mode",current_app_mode)
				previous_checked=current_app_mode
			if previous_freq!=current_freq and output_q_cnt%w1.get()==0:
				comm.write("frame_size",current_freq)
				previous_freq=current_freq
			current_ts=ts1.get()
			if previous_ts!=current_ts and output_q_cnt%w1.get()==0:
				comm.write("timeslice",current_ts)
				previous_ts=current_ts
			# current_sched = sched.get()
			# if previous_sched!=current_sched:
			# 	comm.write("sched",current_sched)
			# 	previous_sched=current_sched
			# fps.update()
			master.update_idletasks()
			master.update()
			key = cv2.waitKey(1) & 0xFF
			# if the `q` key was pressed, break from the loop
			if key == ord("q"):
				break
			if output_q_cnt==0:
				checked.set(str(sys.argv[8]))
			if object_detected == 'person' and w1.get()!=FSIZE[1][1]:
				w1.set(FSIZE[1][1])
			if object_detected == 'car' and w1.get()!=FSIZE[0][1] :
				w1.set(FSIZE[0][1])
			if object_detected == 'cat' and w1.get()!=FSIZE[0][1] :
				w1.set(FSIZE[0][1])
			# if catlen==0: 
			# 	if output_q_cnt==0: 
			# 		 checked.set(str(sys.argv[8]))
			# 	if "RT" in sys.argv[7]:
			# 		if output_q_cnt == onecatvidlen:
			# 			w1.set(FSIZE[0][1])
			# 			sock_client.send(bytes('L','UTF-8'))

			# 		if output_q_cnt == 2*onecatvidlen:
			# 			w1.set(FSIZE[1][1])
			# 			sock_client.send(bytes('M','UTF-8'))
			# 	else:
			# 		if remotetrack>0 and remotetrack!=w1.get():
			# 			w1.set(remotetrack)

			# else:
			# 	if output_q_cnt==0: 
			# 		 checked.set(str(sys.argv[8]))
			# 	if output_q_cnt == onecatvidlen:
			# 		w1.set(FSIZE[0][1])
			# 	if output_q_cnt == 2*onecatvidlen:
			# 		w1.set(FSIZE[1][1])			




			
# stop the timer and display FPS information
# fps.stop()
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

# if remotetrack!=-1:
# 	sock_client.send(bytes('clean_up','UTF-8'))

