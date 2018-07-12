import heartbeat
import numpy as np

window_size_hr=5
hb = heartbeat.Heartbeat(1024,window_size_hr,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode","frame_size","timeslice"]
comm = heartbeat.DomU(monitoring_items)


it = 500
matsize = 500
comm.write("app_mode", 2)
comm.write("frame_size", matsize)
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

comm.write("heart_rate", "done")
hb.heartbeat_finish()