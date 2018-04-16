import heartbeat
import threading
import sys
from pyxs import Client
import time
import numpy as np

window_size_hr=5
hb = heartbeat.Heartbeat(1024,window_size_hr,1000,"vic.log",10,1000)
# #            shm_key, win_size,buf_depth,log_file,min_target,max_target):
monitoring_items = ["heart_rate","app_mode","frame_size"]
comm = heartbeat.DomU(monitoring_items)
# print("start")
st = time.time()

a = []
for i in range(400):
	a.append([])
	for j in range(400):
		a[i].append(j+1)
a=np.asarray(a)
b=np.asarray(a)

# print(b)
# a= np.random.rand(500, 500)
# b= np.random.rand(500, 500)	

it = 500
matsize = 500
comm.write("app_mode", 2)
comm.write("frame_size", matsize)


try:
	for i in range(it*6):
	# hb stuff
		a= np.random.rand(matsize, matsize)
		b= np.random.rand(matsize, matsize)	
		# c= np.dot(b,a.T)
		# tn = time.time()
		c= np.matmul(b,a.T)
		# print(time.time()-tn)

		# time.sleep(0.1)
		hb.heartbeat_beat()
		if i%window_size_hr==0:
			comm.write("heart_rate", hb.get_window_heartrate())

		if i==it*0+10:
			comm.write("app_mode", 1)
		elif i==it*1:
			matsize=600
			comm.write("frame_size", matsize)

		elif i==it*2:
			comm.write("app_mode", 2)
			matsize=500
			comm.write("frame_size", matsize)
		elif i==it*2+10:
			comm.write("app_mode", 3)
		elif i==it*3:
			matsize=600
			comm.write("frame_size", matsize)


		elif i==it*4:
			comm.write("app_mode", 2)
			matsize=500
			comm.write("frame_size", matsize)
		elif i==it*4+10:
			comm.write("app_mode", 4)
		elif i==it*5:
			matsize=600
			comm.write("frame_size", matsize)


# hb.heartbeat_beat()
# comm.write("heart_rate","reset")

it = 500
matsize = 500
comm.write("app_mode", 2)
comm.write("frame_size", matsize)
try:
	for i in range(it*6):
	# hb stuff
		a= np.random.rand(matsize, matsize)
		b= np.random.rand(matsize, matsize)	
		# c= np.dot(b,a.T)
		# tn = time.time()
		c= np.matmul(b,a.T)
		# print(time.time()-tn)

		# time.sleep(0.1)
		hb.heartbeat_beat()
		if i%window_size_hr==0:
			comm.write("heart_rate", hb.get_window_heartrate())

		if i==it*0+10:
			comm.write("app_mode", 1)
		elif i==it*1:
			matsize=600
			comm.write("frame_size", matsize)

		elif i==it*2:
			comm.write("app_mode", 2)
			matsize=500
			comm.write("frame_size", matsize)
		elif i==it*2+10:
			comm.write("app_mode", 3)
		elif i==it*3:
			matsize=600
			comm.write("frame_size", matsize)


		elif i==it*4:
			comm.write("app_mode", 2)
			matsize=500
			comm.write("frame_size", matsize)
		elif i==it*4+10:
			comm.write("app_mode", 4)
		elif i==it*5:
			matsize=600
			comm.write("frame_size", matsize)



except:
	print("stopped")
	comm.write("heart_rate", "done")

# hb.heartbeat_beat()

# print(hb.get_global_heartrate())
# print(1/hb.get_global_heartrate())



hb.heartbeat_finish()