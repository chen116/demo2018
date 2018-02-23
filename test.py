from ctypes import cdll
import ctypes
import sysv_ipc
import sys

import time
import _thread

shmlib = cdll.LoadLibrary('./shmlib.so')
ids = [1024]

lenn = len(ids)
logids=[]
gloids=[]
for x in ids:
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
	shmlib.heartbeat_init(hb,vic_win_size,vic_buf_depth,vic_log_file,vic_min_target,vic_max_target)
logmem = []
glomem = []
result = None
while result is None:
	try:
		for i in range(lenn):
			logmem.append(sysv_ipc.SharedMemory(logids[i]))
			glomem.append(sysv_ipc.SharedMemory(gloids[i]))
			result=1
	except:
		pass

cnt=-1
while cnt<10:
	cnt+=1
	time.sleep(1)
	for i in range(lenn):
		p=logmem[i].read()
		shmlib.heartbeat.restype = ctypes.c_int64
		hbtime = shmlib.heartbeat(hbids[i],cnt)
		hr = shmlib.get_hr(p,tmp_index)/1e6
		print('hbtime',hbtime,'hr','hr')
for i in range(lenn):
	shmlib.heartbeat_finish(hbids[i])






crement=int(1e5/10)
keep_going =[1 for x in range(lenn)]
indexs = [0 for x in range(lenn)]
cs=[]
cpu_quotas = [crement*2 for x in range(lenn)]
while sum(keep_going)>0:
	if len(cs)!=len(ids):
		cs=client.containers.list()
		lenn=len(cs)
		cs.reverse()
	if len(cs)>0:
		for i in range(lenn):
			if keep_going[i]:
				g=glomem[i].read()
				tmp_index = shmlib.get_index(g)
				if tmp_index!=indexs[i]:
					indexs[i]=tmp_index
					# print("v",i,indexs[i])
					if indexs[i]>=30:
						keep_going[i]=0
					if i==1 and indexs[i]>=30:
						keep_going[i]=0
						for con in client.containers.list():
							if con.name=='v'+str(i):
								con.remove(force=True)
					p=logmem[i].read()
					hr = shmlib.get_hr(p,tmp_index)/1e6
					shmlib.get_ts.restype = ctypes.c_int64
					ts = shmlib.get_ts(p,tmp_index)
					if i==0:
						print("    v",i,"index",tmp_index,"ts", ts,"hr",hr,"cpu",cpu_quotas[i])
					else:
						print(" v",i,"index",tmp_index,"ts", ts,"hr",hr,"cpu",cpu_quotas[i])
					# if i==0:
					# 	if hr<1.5:
					# 		cpu_quotas[i]+=int(crement)
					# 		if cpu_quotas[i]>=40000:
					# 			cpu_quotas[i]=40000
					# 		cs[i].update(cpu_period=int(crement),cpu_quota=cpu_quotas[i])
					# 	if hr>2.0:
					# 		cpu_quotas[i]-=int(crement)
					# 		if cpu_quotas[i]<=0:
					# 			cpu_quotas[i]=crement
					# 		cs[i].update(cpu_period=int(crement),cpu_quota=cpu_quotas[i])
					# else:
					# 	if hr<0.75:
					# 		cpu_quotas[i]+=int(crement)
					# 		cs[i].update(cpu_period=int(crement),cpu_quota=cpu_quotas[i])
					# 	if hr>1.:
					# 		cpu_quotas[i]-=int(crement)
					# 		if cpu_quotas[i]<=0:
					# 			cpu_quotas[i]=crement
					# 		cs[i].update(cpu_period=int(crement),cpu_quota=cpu_quotas[i])						




# for i in range(lenn):
# 	p=logmem[i].read()
# 	g=glomem[i].read()
# 	fname_index=i
# 	shmlib.write_vlog(p,g,fname_index)
print("dynamo done")






# sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q)
