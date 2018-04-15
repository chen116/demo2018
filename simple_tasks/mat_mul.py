import heartbeat
import threading
import sys
from pyxs import Client
import time
import numpy as np

window_size_hr=5
hb = heartbeat.Heartbeat(1024,window_size_hr,1000,"vic.log",10,1000)
# #            shm_key, win_size,buf_depth,log_file,min_target,max_target):
monitoring_items = ["heart_rate","app_mode"]
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
try:
	for i in range(500):
	# hb stuff
		# c= np.dot(b,a.T)
		# c= np.matmul(b,a.T)
		time.sleep(0.1)
		hb.heartbeat_beat()

		comm.write("heart_rate", hb.get_instant_heartrate())
except:
	print("stopped")
	comm.write("heart_rate", "done")

# hb.heartbeat_beat()
# comm.write("heart_rate","reset")



# hb.heartbeat_beat()

# print(hb.get_global_heartrate())
# print(1/hb.get_global_heartrate())



hb.heartbeat_finish()