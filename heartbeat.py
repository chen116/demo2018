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
	def get_global_heartrate(self):
		self.heartbeat_python_lib.get_global_heartrate.restype = ctypes.c_double
		return self.heartbeat_python_lib.get_global_heartrate(self.shm_key,self.cnt)
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
			# c.write(self.key_path_hash[key],msg)
			success = False
			while not success:
				c.transaction()
				c.write(self.key_path_hash[key],msg)
				success = c.commit()
	def wait_till_val_read(self,key,desired_val):
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			msg = desired_val-1
			while msg!=desired_val:
				try:
					msg=int(c.read(self.key_path_hash[key]).decode())
				except:
					msg=desired_val-1
	def read(self,key):
		msg=0
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			try:
				msg=int(c.read(self.key_path_hash[key]).decode())
			except:
				msg=-1
		return msg