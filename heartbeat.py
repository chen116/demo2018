from ctypes import cdll
import ctypes
import sysv_ipc
import sys
from pyxs import Client
import threading
import xen_interface



class Heartbeat:
	def __init__(self,shm_key, win_size,buf_depth,log_file,min_target,max_target):
		self.win_size = win_size
		self.buf_depth = buf_depth
		self.log_file = log_file.encode('utf-8')
		self.min_target = min_target
		self.max_target = max_target
		self.shm_key = shm_key
		self.heartbeat_python_lib = cdll.LoadLibrary('./heartbeat_python_lib.so')
		self.cnt = -1
		
		# conversion is from hearbeat code
		log_shm_key = self.shm_key*2
		state_shm_eky = self.shm_key*2+1
		# remove exsisting shm
		shm_ids = [shm_key ,log_shm_key, state_shm_eky]
		for tmp_shm_key in shm_ids:
			try:
				memory = sysv_ipc.SharedMemory(tmp_shm_key)
			except sysv_ipc.ExistentialError:
				print('''The shared memory with tmp_shm_key "{}" doesn't exist.'''.format(tmp_shm_key))
			else:
				memory.remove()
				print('Removed the shared memory with tmp_shm_key "{}".'.format(tmp_shm_key))
		self.heartbeat_python_lib.anchors_heartbeat_init.argtypes = [ctypes.c_int,ctypes.c_int64,ctypes.c_int64,ctypes.c_char_p,ctypes.c_double,ctypes.c_double ]
		suc = self.heartbeat_python_lib.anchors_heartbeat_init(self.shm_key,self.win_size,self.buf_depth,self.log_file,self.min_target,self.max_target)
		if suc:
			print("hb_init!")	
	def heartbeat_beat(self):
		self.cnt=(self.cnt+1)%self.buf_depth
		self.heartbeat_python_lib.anchors_heartbeat.restype = ctypes.c_int64
		hbtime = self.heartbeat_python_lib.anchors_heartbeat(self.shm_key,self.cnt) # hbtime/1e9 = seconds
	def get_instant_heartrate(self):
		self.heartbeat_python_lib.get_instant_heartrate.restype = ctypes.c_double
		return self.heartbeat_python_lib.get_instant_heartrate(self.shm_key,self.cnt)
	def get_window_heartrate(self):
		self.heartbeat_python_lib.get_window_heartrate.restype = ctypes.c_double
		return self.heartbeat_python_lib.get_window_heartrate(self.shm_key,self.cnt)
	def heartbeat_finish(self):
		if self.heartbeat_python_lib.anchors_heartbeat_finish(self.shm_key):
			print("clean up",self.shm_key)




class Dom0:
	def __init__(self,keys=['heart_rate'],domu_ids=[],base_path='/local/domain'):
		self.domu_ids = domu_ids
		self.keys=keys
		self.base_path=base_path
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			if domu_ids==[]:
				for x in c.list(base_path.encode()):
					self.domu_ids.append(x.decode())
				self.domu_ids.pop(0)
			for domuid in self.domu_ids:
				permissions = []
				permissions.append(('b'+'0').encode())
				permissions.append(('b'+domuid).encode())
				for key in keys:
					tmp_key_path = (base_path+'/'+domuid+'/'+key).encode()
					tmp_val = ('xenstore entry init').encode()
					c.write(tmp_key_path,tmp_val)
					c.set_perms(tmp_key_path,permissions)
					print('created',key,'for dom',domuid)
	# def monitor(self, domuid):  # one monitor observe one domU at a time
	# 	with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
	# 		m = c.monitor()
	# 		for key in self.keys:
	# 			tmp_key_path = (self.base_path+'/'+domuid+'/'+key).encode()
	# 			token = (key+' '+domuid).encode()
	# 			m.watch(tmp_key_path,token)
	# 			print('watching',key,'of dom',domuid)
	# 		num_done = 0
	# 		while num_done < len(self.domu_ids):
	# 			path,token=next(m.wait())
	# 			msg=c.read(path).decode()
	# 			print( token.decode(),':',msg)
	# 			if msg=='q':
	# 				num_done+=1
	# def monitor(self):  # one monitor observe all domUs
	# 	with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
	# 		m = c.monitor()
	# 		for domuid in self.domu_ids:
	# 			for key in self.keys:
	# 				tmp_key_path = (self.base_path+'/'+domuid+'/'+key).encode()
	# 				token = (key+' '+domuid).encode()
	# 				m.watch(tmp_key_path,token)
	# 				print('watching',key,'of dom',domuid)
	# 		num_done = 0
	# 		while num_done < len(self.domu_ids):
	# 			path,token=next(m.wait())
	# 			msg=c.read(path).decode()
	# 			print( token.decode(),':',msg)
	# 			if msg=='done':
	# 				num_done+=1
class DomU:
	def __init__(self,keys=['test'],base_path='/local/domain'):
		self.domu_id=""
		self.keys=keys
		self.base_path=base_path
		self.key_path_hash = {}
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			self.domu_id = c.read("domid".encode())
			for key in self.keys:
				self.key_path_hash[key]=(self.base_path+'/'+self.domu_id.decode()+'/'+key).encode()
	def write(self,key='test',val='0'):
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			msg=str(val).encode()
			c.write(self.key_path_hash[key],msg)



class MonitorThread(threading.Thread):
	def __init__(self, threadLock,shared_data,res_allo,domuid,sched,min_heart_rate,max_heart_rate,keys=['test'],base_path='/local/domain'):
		threading.Thread.__init__(self)
		self.domuid=(domuid)
		self.keys=keys
		self.base_path=base_path
		self.threadLock=threadLock
		self.shared_data=shared_data
		self.res_allo=res_allo
		self.anchors = 0
		self.sched = sched
		self.target_reached_cnt = 0
		self.min_heart_rate=min_heart_rate
		self.max_heart_rate=max_heart_rate
	def run(self):
		# Acquire lock to synchronize thread
		# self.threadLock.acquire()
		self.vmonitor()
		# Release lock for the next thread
		# self.threadLock.release()
		print("Exiting " , self.name)
	def vmonitor(self):  # one monitor observe one domU at a time
		with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
			m = c.monitor()
			for key in self.keys:
				tmp_key_path = (self.base_path+'/'+self.domuid+'/'+key).encode()
				token = (key).encode()
				m.watch(tmp_key_path,token)

			msg=""
			while msg!='done':
				path,token=next(m.wait())
				msg=c.read(path).decode()
				self.threadLock.acquire()
				if self.keys[1] in path.decode():
					if msg.isdigit():
						self.anchors = int(msg)
						with open("info.txt", "a") as myfile:
							myfile.write(self.domuid+" "+(msg)+"\n")
				if self.keys[2] in path.decode():
					if msg.isdigit():
						with open("info.txt", "a") as myfile:
							myfile.write(self.domuid+" "+(msg)+" frame size"+"\n")

				if self.keys[0] in path.decode():
					heart_rate=-1
					try :
						heart_rate = float(msg)
					except:
						heart_rate=-1
					if heart_rate>-1:
						self.res_allocat(heart_rate)					
						#self.res_allo(self.anchors,self.sched,float(msg),self.shared_data,self.domuid ,self.min_heart_rate,self.max_heart_rate)					

				# try :
				# 	if self.keys[0] in path.decode():
				# 		self.res_allocat(float(msg))					
				# 		#self.res_allo(self.anchors,self.sched,float(msg),self.shared_data,self.domuid ,self.min_heart_rate,self.max_heart_rate)					
				# except:
				# 	print("meow",int(self.domuid),token.decode(),msg)

				self.threadLock.release()

				# print( token.decode(),':',msg)
	def res_allocat(self,heart_rate):
		tab='               dom '+str(int(self.domuid))
		if int(self.domuid)<2:
			tab='dom '+str(int(self.domuid))
		print(tab,'heart_rate',heart_rate)



		if self.anchors==1:
			if self.sched==1:
				print(tab,'RT-Xen anchors ACTIVE:')
				cur_b = 0
				myinfo = self.shared_data[self.domuid]
				for vcpu in myinfo:
					if vcpu['pcpu']!=-1:
						cur_b=int(vcpu['b'])

				if(heart_rate<self.min_heart_rate):
					if cur_b<=9800:
						cur_b+=100
						xen_interface.sched_rtds(self.domuid,10000,cur_b,[])
						xen_interface.sched_rtds(str(int(self.domuid)+2),10000,10000-cur_b,[])
				if(heart_rate>self.max_heart_rate):
					if cur_b>=200:
						cur_b-=100
						xen_interface.sched_rtds(self.domuid,10000,cur_b,[])
						xen_interface.sched_rtds(str(int(self.domuid)+2),10000,10000-cur_b,[])


				# if heart_rate<=max_heart_rate && heart_rate >= self.min_heart_rate:
				# 	target_reached_cnt+=1
				# 	if target_reached_cnt==10:
				# 		target_reached_cnt=0

				myinfo = self.shared_data[self.domuid]
				cnt=0
				for vcpu in myinfo:
					if vcpu['pcpu']!=-1:
						vcpu['b']=cur_b
						print(tab,'vcpu:',cnt,'b:',vcpu['b'])
						cnt+=1
			else:
				print(tab,'Credit anchors ACTIVE:')
				cur_w = 0
				myinfo = self.shared_data[self.domuid]
				for vcpu in myinfo:
					if vcpu['pcpu']!=-1:
						cur_w=int(vcpu['w'])

				if(heart_rate<self.min_heart_rate):
					if cur_w<=9800:
						cur_w+=100
						xen_interface.sched_credit(self.domuid,cur_w)
						xen_interface.sched_credit(str(int(self.domuid)+2),10000-cur_w)
				if(heart_rate>self.max_heart_rate):
					if cur_w>=200:
						cur_w-=100
						xen_interface.sched_credit(self.domuid,cur_w)
						xen_interface.sched_credit(str(int(self.domuid)+2),10000-cur_w)
				myinfo = self.shared_data[self.domuid]
				cnt=0
				for vcpu in myinfo:
					if vcpu['pcpu']!=-1:
						vcpu['w']=cur_w
						print(tab,'vcpu:',cnt,'w:',vcpu['w'])
						cnt+=1


		else:
			if self.sched==1:
				print(tab,'-------------RT-Xen anchors INACTIVE:')
				default_b=5000
				myinfo = self.shared_data[self.domuid]
				cnt=0
				not_default_b = 0
				for vcpu in myinfo:
					if vcpu['pcpu']!=-1:
						if vcpu['b']!=default_b:
							not_default_b = 1
							vcpu['b']=default_b

						print(tab,'vcpu:',cnt,'b:',vcpu['b'])	
						cnt+=1
				if not_default_b:
					xen_interface.sched_rtds(self.domuid,10000,default_b,[])
					xen_interface.sched_rtds(str(int(self.domuid)+2),10000,default_b,[])
			else:
				print(tab,'Credit anchors INACTIVE:')
				default_w=5000
				myinfo = self.shared_data[self.domuid]
				cnt=0
				not_default_w = 0
				for vcpu in myinfo:
					if vcpu['pcpu']!=-1:
						if vcpu['w']!=default_w:
							not_default_w = 1
							vcpu['w']=default_w

						print(tab,'vcpu:',cnt,'w:',vcpu['w'])	
						cnt+=1
				if not_default_w:
					xen_interface.sched_credit(self.domuid,default_w)
					xen_interface.sched_credit(str(int(self.domuid)+2),default_w)
		buf=10000
		self.shared_data['cnt'] = (self.shared_data['cnt']+1)%buf
		info = self.domuid+" "+str(heart_rate)+" "
		if self.sched==1:
			info += str(self.shared_data[self.domuid][0]['b'])
		else:
			info += str(self.shared_data[self.domuid][0]['w'])


		if self.shared_data['cnt']%buf!=0:
			with open("info.txt", "a") as myfile:
				myfile.write(info+"\n")
		else:
			with open("info.txt", "w") as myfile:
				myfile.write(info+"\n")



		return
	# https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
	# cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list

