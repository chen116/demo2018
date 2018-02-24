from ctypes import cdll
import ctypes
import sysv_ipc
import sys

class Heartbeat:
	def __init__(self,pid, win_size,buf_depth,log_file,min_target,max_target):
		self.win_size = win_size
		self.buf_depth = buf_depth
		self.log_file = log_file
		self.min_target = min_target
		self.max_target = max_target
		self.pid = pid
		self.shmlib = cdll.LoadLibrary('./shmlib.so')
		self.cnt = 0
		pids = [pid]
		lenn = len(pids)
		logids=[]
		gloids=[]
		for x in pids:
			logids.append(x*2)
			gloids.append(x*2+1)
		# remove shm
		for i in range(lenn):
			key=logids[i]
			try:
			    memory = sysv_ipc.SharedMemory(key)
			except sysv_ipc.ExistentialError:
			    print('''The shared memory with key "{}" doesn't exist.'''.format(key))
			else:
			    memory.remove()
			    print('Removed the shared memory with key "{}".'.format(key))
			key=gloids[i]
			try:
			    memory = sysv_ipc.SharedMemory(key)
			except sysv_ipc.ExistentialError:
			    print('''The shared memory with key "{}" doesn't exist.'''.format(key))
			else:
			    memory.remove()
			    print('Removed the shared memory with key "{}".'.format(key))
			key=pids[i]
			try:
			    memory = sysv_ipc.SharedMemory(key)
			except sysv_ipc.ExistentialError:
			    print('''The shared memory with key "{}" doesn't exist.'''.format(key))
			else:
			    memory.remove()
			    print('Removed the shared memory with key "{}".'.format(key))
		suc = self.shmlib.anchors_heartbeat_init(self.pid,self.win_size,self.buf_depth,self.log_file,self.min_target,self.max_target)
		if suc:
			print("hb_init!")	
	def heartbeat_beat(self):
		self.shmlib.anchors_heartbeat.restype = ctypes.c_int64
		hbtime = self.shmlib.anchors_heartbeat(self.pid,self.cnt)
		hr = self.shmlib.get_hr_from_hb(self.pid,self.cnt)/1e6
		self.cnt+=1
		print('hbtime',hbtime/1e9,'hr',hr)
	def heartbeat_finish(self):
		if self.shmlib.anchors_heartbeat_finish(self.pid):
			print("clean up",self.pid)


