from ctypes import cdll
import ctypes
import sysv_ipc
import sys

import time
import _thread

shmlib = cdll.LoadLibrary('./shmlib.so')
pids = [1024]

lenn = len(pids)
logids=[]
gloids=[]
hbids=[]
for x in pids:
	hbids.append(int(x/2))
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
	key=hbids[i]
	try:
	    memory = sysv_ipc.SharedMemory(key)
	except sysv_ipc.ExistentialError:
	    print('''The shared memory with key "{}" doesn't exist.'''.format(key))
	else:
	    memory.remove()
	    print('Removed the shared memory with key "{}".'.format(key))

vic_win_size = 10;
vic_buf_depth = 1000;
vic_log_file ="vic.log";
vic_min_target = 100;
vic_max_target = 1000;
for i in range(lenn):
	suc = shmlib.anchors_heartbeat_init(hbids[i],pids[i],vic_win_size,vic_buf_depth,vic_log_file,vic_min_target,vic_max_target)
	if suc:
		print("hb_init!")
logmem = []
glomem = []
result = None

try:
	for i in range(lenn):
		logmem.append(sysv_ipc.SharedMemory(logids[i]))
		glomem.append(sysv_ipc.SharedMemory(gloids[i]))
		result=1
except Exception as e: 
	print(e)
	print("nooo")
	pass

cnt=-1
while cnt<10:
	cnt+=1
	time.sleep(1)
	for i in range(lenn):
		p=logmem[i].read()
		shmlib.anchors_heartbeat.restype = ctypes.c_int64
		hbtime = shmlib.anchors_heartbeat(hbids[i],cnt)
		hr = shmlib.get_hr(p,cnt)/1e6
		print('hbtime',hbtime,'hr',hr)
for i in range(lenn):
	shmlib.anchors_heartbeat_finish(pids[i])



