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
while True:
# hb stuff
	for i in range(int(1e2)):
		a= np.random.rand(500, 500)
		b= np.random.rand(500, 500)	
		c= np.dot(b,a.T)
	hb.heartbeat_beat()
	comm.write("heart_rate", hb.get_window_heartrate())

# hb.heartbeat_beat()
# comm.write("heart_rate","reset")



# hb.heartbeat_beat()

# print(hb.get_global_heartrate())
# print(1/hb.get_global_heartrate())



hb.heartbeat_finish()