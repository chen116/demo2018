


# thruput

import heartbeat
import threading
import sys
from pyxs import Client
import time
import numpy as np









lat_or_thruput=sys.argv[1]

# thruput
if 'thru' in lat_or_thruput:
	window_size_hr=5
	hb = heartbeat.Heartbeat(1024,window_size_hr,100,"vic.log",10,100)
	#             shm_key, win_size,buf_depth,log_file,min_target,max_target):
	monitoring_items = ["heart_rate","app_mode"]
	comm = heartbeat.DomU(monitoring_items)
	print("start")
	for i in range(100-1):
	# hb stuff
		hb.heartbeat_beat()
		# window_hr = hb.get_window_heartrate()
		comm.write("heart_rate",i)
	# #print("hb: before get_instant_heartrate()")
	comm.write("app_mode","reset")

	hb.heartbeat_finish()
else:
	class MonitorThread(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.timestamps=[]
			with Client(xen_bus_path="/dev/xen/xenbus") as c:
				self.domu_id = c.read("domid".encode())
				self.key_path_hash=('/local/domain/'+self.domu_id.decode()+'/app_mode').encode()
		def run(self):

			with Client(xen_bus_path="/dev/xen/xenbus") as c:
				msg = -1
				tmp_msg = -1
				while msg!=0:
					try:
						msg = int(c.read(self.key_path_hash).decode())
						self.timestamps.append(time.time())
						# print(msg)
					except:
						msg = -1
				tmp_msg=msg
				while tmp_msg!=100-1:
					msg = int(c.read(self.key_path_hash).decode())
					if msg!=tmp_msg:
						tmp_msg=msg
						self.timestamps.append(time.time())
						# print(msg)
				c.write(self.key_path_hash, 'reset'.encode())




	tmp_thread = MonitorThread()
	tmp_thread.start()


	tx_timestamps=[]
	hb_timestamps=[]
	window_size_hr=5
	hb = heartbeat.Heartbeat(1024,window_size_hr,100,"vic.log",10,100)
	#             shm_key, win_size,buf_depth,log_file,min_target,max_target):
	monitoring_items = ["heart_rate","app_mode"]
	comm = heartbeat.DomU(monitoring_items)

	for i in range(100):
	# hb stuff

		hb_timestamps.append(time.time())
		hb.heartbeat_beat()
		# window_hr = hb.get_window_heartrate()
		tx_timestamps.append(time.time())
		comm.write("heart_rate",str(i))

	# #print("hb: before get_instant_heartrate()")





	tmp_thread.join()
	rx_timestamps = tmp_thread.timestamps
	hb.heartbeat_finish()
	hbs = np.asarray(hb_timestamps)
	txs = np.asarray(tx_timestamps)
	rxs = np.asarray(rx_timestamps)

	print(hbs.shape)
	print(txs.shape)
	print(rxs.shape)


	print( np.average((rxs-txs)/2+(txs-hbs)))
	# print(rx_timestamps)

			


# #print("hb: after hb stuff")
# if global_cnt>window_size_hr:
# 	comm.write("heart_rate",window_hr)
# # #print('------------------window_hr:',window_hr)
# # #print('instant_hr:',instant_hr)
# current_checked = checked.get()
# if previous_checked!=current_checked:
# 	comm.write("app_mode",current_checked)
# 	previous_checked=current_checked
# if previous_f_size!=current_f_size:
# 	comm.write("frame_size",current_f_size)
# 	previous_f_size=current_f_size
# current_ts=ts1.get()
# if previous_ts!=current_ts:
# 	comm.write("timeslice",current_ts)
# 	previous_ts=current_ts