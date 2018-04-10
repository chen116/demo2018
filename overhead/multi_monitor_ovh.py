
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
	def __init__(self,domuid):
		threading.Thread.__init__(self)
		self.domuid=(domuid)
		self.base_path='/local/domain'
		self.ovh = 0
		self.ovh_cnt=0


	def run(self):
		# Acquire lock to synchronize thread
		# self.threadLock.acquire()

		# Release lock for the next thread
		# self.threadLock.release()
		#print("Exiting " , self.name)

		with Client() as c:
		# with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
			m = c.monitor()
			self.watch_tmp_key_path = (self.base_path+'/'+self.domuid+'/heart_rate').encode()
			self.write_tmp_key_path = (self.base_path+'/'+self.domuid+'/app_mode').encode()
			print(c.write(self.write_tmp_key_path).decode())
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



for domuid in c.domu_ids:
	tmp_thread = MonitorThread(domuid)
	tmp_thread.start()
	threads.append(tmp_thread)


# Wait for all MonitorThreads to complete
threads_cnt=0
for t in threads:
	t.join()
	threads_cnt+=1
print('done')