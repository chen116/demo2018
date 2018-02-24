from ctypes import cdll
import ctypes
import sysv_ipc
import sys

class Heartbeat:
	def __init__(self,shm_key, win_size,buf_depth,log_file,min_target,max_target):
		self.win_size = win_size
		self.buf_depth = buf_depth
		self.log_file = log_file.encode('utf-8')
		self.min_target = min_target
		self.max_target = max_target
		self.shm_key = shm_key
		self.shmlib = cdll.LoadLibrary('./shmlib.so')
		self.hb_cnt = -1
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
		self.shmlib.anchors_heartbeat_init.argtypes = [ctypes.c_int,ctypes.c_int64,ctypes.c_int64,ctypes.c_char_p,ctypes.c_double,ctypes.c_double ]
		suc = self.shmlib.anchors_heartbeat_init(self.shm_key,self.win_size,self.buf_depth,self.log_file,self.min_target,self.max_target)
		if suc:
			print("hb_init!")	
	def heartbeat_beat(self):
		self.hb_cnt+=1
		self.shmlib.anchors_heartbeat.restype = ctypes.c_int64
		hbtime = self.shmlib.anchors_heartbeat(self.shm_key,self.hb_cnt) # hbtime/1e9 = seconds
	def get_instant_heartrate(self):
		hr = self.shmlib.get_instant_heartrate(self.shm_key,self.hb_cnt)/1e6
		return hr
	def heartbeat_finish(self):
		if self.shmlib.anchors_heartbeat_finish(self.shm_key):
			print("clean up",self.shm_key)


