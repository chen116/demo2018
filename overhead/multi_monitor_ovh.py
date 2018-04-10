
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time
import pprint
import sys
from pyxs import Client



with open("info.txt", "w") as myfile:
	myfile.write("")

monitoring_items = ["heart_rate","app_mode"]
# c = heartbeat.Dom0(monitoring_items,['1','2','3','4'])
c = heartbeat.Dom0(monitoring_items,['1'])





class MonitorThread(threading.Thread):
	def __init__(self, threadLock,shared_data,domuid,sched,timeslice_us,min_heart_rate,max_heart_rate,keys=['test'],base_path='/local/domain'):
		threading.Thread.__init__(self)
		self.domuid=(domuid)
		self.keys=keys
		self.base_path=base_path
		self.threadLock=threadLock
		self.shared_data=shared_data
		self.anchors = 0
		self.sched = sched
		self.target_reached_cnt = 0
		self.min_heart_rate=min_heart_rate
		self.max_heart_rate=max_heart_rate
		self.timeslice_us = timeslice_us
		self.ovh = 0
		self.ovh_cnt=0


	def run(self):
		# Acquire lock to synchronize thread
		# self.threadLock.acquire()
		self.vmonitor()
		# Release lock for the next thread
		# self.threadLock.release()
		#print("Exiting " , self.name)
	def vmonitor(self):  # one monitor observe one domU at a time
		with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
			m = c.monitor()
			self.watch_tmp_key_path = (self.base_path+'/'+self.domuid+'/heart_rate').encode()
			self.write_tmp_key_path = (self.base_path+'/'+self.domuid+'/app_mode').encode()
			token = ("heart_rate").encode()
			m.watch(self.watch_tmp_key_path,token)

			msg=""
			while msg!='done':
				path,token=next(m.wait())
				# msg=c.read(path).decode()
				msg=c.read(path)
				# self.threadLock.acquire()		
				if self.ovh_cnt==0:
					heart_rate=-1
					try :
						heart_rate = int(msg.decode())
					except:
						heart_rate=-1
					if heart_rate>-1:
						c.write(self.write_tmp_key_path,msg)
						print(int(msg.decode()))
						self.ovh_cnt=1
						
				else:
					c.write(self.write_tmp_key_path,msg)
					print(int(msg.decode()))



				# if "heart_rate" in path.decode():
				# 	if self.ovh_cnt==0:
				# 		heart_rate=-1
				# 		try :
				# 			heart_rate = float(msg)
				# 		except:
				# 			heart_rate=-1
				# 		if heart_rate>-1:
				# 			self.ovh = time.time()
				# 			# print('first time',self.ovh)
				# 			self.ovh_cnt=1

					

				# self.threadLock.release()
			# print(time.time() - self.ovh)


				# #print( token.decode(),':',msg)






threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()
timeslice_us=15000
default_bw=int(timeslice_us/2)

for domuid in shared_data['rtxen']:
	xen_interface.sched_rtds(domuid,timeslice_us,default_bw,[])
for domuid in shared_data['xen']:
	xen_interface.sched_credit(domuid,default_bw)
shared_data = xen_interface.get_global_info()





min_heart_rate = float(sys.argv[1])
max_heart_rate = float(sys.argv[2])

with open("minmax.txt", "w") as myfile:
	myfile.write("min "+sys.argv[1]+"\n")
	myfile.write("max "+sys.argv[2]+"\n")
	myfile.write("timeslice_us "+str(timeslice_us/1000)+"\n")






for domuid in c.domu_ids:
	tmp_thread = MonitorThread(threadLock,shared_data,domuid,int(domuid)%2,timeslice_us,min_heart_rate,max_heart_rate, monitoring_items)
	tmp_thread.start()
	threads.append(tmp_thread)




# Wait for all MonitorThreads to complete
threads_cnt=0
for t in threads:
	t.join()
	threads_cnt+=1
#print('FINAL COUNT:',shared_data['cnt'])
pp = pprint.PrettyPrinter(indent=2)
print('Final domUs info:')
shared_data = xen_interface.get_global_info()
for domuid in shared_data['rtxen']:
	xen_interface.sched_rtds(domuid,timeslice_us,default_bw,[])
xen_interface.sched_credit_timeslice(timeslice_us/1000)
for domuid in shared_data['xen']:
	xen_interface.sched_credit(domuid,default_bw)
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
print("Restored RT-Xen, Credit to all domUs have equal cpu time sharing")
