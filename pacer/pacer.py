import heartbeat
import host_guest_comm
import numpy as np
import time

window_size_hr=5
hb = heartbeat.Heartbeat(1024,window_size_hr,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode","frame_size","timeslice"]
comm = host_guest_comm.DomU(monitoring_items)


it = 500
matsize = 500
comm.write("app_mode", 2)
comm.write("frame_size", matsize)
for i in range(it*6):
# hb stuff
	a= np.random.rand(matsize, matsize)
	b= np.random.rand(matsize, matsize)	
	tn = time.time()
	c= np.matmul(b,a.T)
	print(time.time()-tn)
	time.sleep(0.1)
	hb.heartbeat_beat()
	print(hb.get_instant_heartrate())
	if i%window_size_hr==0:
		comm.write("heart_rate", hb.get_window_heartrate())



comm.write("heart_rate", "done")
hb.heartbeat_finish()