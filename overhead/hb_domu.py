


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
	hb = heartbeat.Heartbeat(1024,window_size_hr,1000,"vic.log",10,1000)
	# #            shm_key, win_size,buf_depth,log_file,min_target,max_target):
	monitoring_items = ["heart_rate","app_mode"]
	comm = heartbeat.DomU(monitoring_items)
	# print("start")
	st = time.time()
	for i in range(int(1e2)):
	# hb stuff
		# a= np.random.rand(500, 500)
		# b= np.random.rand(500, 500)	
		# c= np.dot(b,a.T)
		hb.heartbeat_beat()
		comm.write("heart_rate",i)

	# hb.heartbeat_beat()
	# comm.write("heart_rate","reset")


	time_now = time.time()

	print(int(1e2)/(time_now-st))
	print( (time_now-st)/int(1))

	# hb.heartbeat_beat()

	# print(hb.get_global_heartrate())
	# print(1/hb.get_global_heartrate())



	hb.heartbeat_finish()
else:
	class MonitorThread(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.rx_timestamps=[0 for i in range(1000)]
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
						# self.rx_timestamps.append(time.time())
						self.rx_timestamps[msg]=(time.time())
						print(msg)
					except:
						msg = -1
				tmp_msg=msg
				while tmp_msg!=1000-1:
					msg = int(c.read(self.key_path_hash).decode())
					if msg!=tmp_msg:
						tmp_msg=msg
						# self.rx_timestamps.append(time.time())
						self.rx_timestamps[msg]=(time.time())
						print(msg)
				c.write(self.key_path_hash, 'reset'.encode())





	# window_size_hr=5
	# hb = heartbeat.Heartbeat(1024,window_size_hr,10,"vic.log",10,10)
	#             shm_key, win_size,buf_depth,log_file,min_target,max_target):
	monitoring_items = ["heart_rate","app_mode"]
	comm = heartbeat.DomU(monitoring_items)


	# tmp_thread = MonitorThread()
	# tmp_thread.start()
	key_path_hash=None
	with Client(xen_bus_path="/dev/xen/xenbus") as c:
		domu_id = c.read("domid".encode())
		key_path_hash=('/local/domain/'+domu_id.decode()+'/app_mode').encode()

	tx_timestamps=[]
	hb_timestamps=[]
	rx_timestamps=[0 for i in range(1000)]
	with Client(xen_bus_path="/dev/xen/xenbus") as c:
		for i in range(1000):
		# hb stuff

			# hb_timestamps.append(time.time())
			# hb.heartbeat_beat()
			# window_hr = hb.get_window_heartrate()
			# hb_timestamps.append(time.time())
			comm.write("heart_rate",str(i))
			tx_timestamps.append(time.time())
			msg=-1
			while msg!=i:
				try:
					msg = int(c.read(key_path_hash).decode())
					# self.rx_timestamps.append(time.time())

					rx_timestamps[msg]=(time.time()) if rx_timestamps[msg]!=0 else 0
					# print(msg)
				except:
					msg = -1

		# print(i)
	with Client(xen_bus_path="/dev/xen/xenbus") as c:
		c.write(key_path_hash, 'reset'.encode())


# #print("hb: before get_instant_heartrate()")





	# tmp_thread.join()
	# rx_timestamps = tmp_thread.rx_timestamps
	hbs = np.asarray(hb_timestamps)
	valid_indecies= [i for i, x in enumerate(rx_timestamps) if x != 0]

	txs = []
	rxs = []
	for x in valid_indecies:
		txs.append(tx_timestamps[x])
		rxs.append(rx_timestamps[x])



	txs = np.asarray(txs)
	rxs = np.asarray(rxs)




	print(hbs.shape)
	print(txs.shape)
	print(rxs.shape)
	# hb.heartbeat_beat()

	# print(hb.get_global_heartrate())
	# print(1/hb.get_global_heartrate())



	# print( np.average((rxs-txs)/2+(txs-hbs)))

	print(np.average((rxs-txs)/2))
	print(((rxs-txs)/2))

		# print(rx_timestamps)
	# hb.heartbeat_finish()

			
