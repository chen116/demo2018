from ctypes import cdll
# import ctypes
import sysv_ipc
import sys
import docker
import time
import _thread


# bodytrack /benches/parsec-vic/sequenceB_261/ 4 261 3000 8 2 4 1


# create shm id key


ids = [1000,3000]#, 4000, 5000]


lenn = len(ids)
logids=[]
gloids=[]
for x in ids:
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


# create shm
# for i in range(lenn):
# 	print(logids[i])
# 	logmem.append(sysv_ipc.SharedMemory(logids[i],sysv_ipc.IPC_CREX))
# 	glomem.append(sysv_ipc.SharedMemory(gloids[i],sysv_ipc.IPC_CREX))
shmlib = cdll.LoadLibrary('./shmlib.so')
for i in range(lenn):
	shmlib.setshm_glo(gloids[i])
	shmlib.setshm_log(logids[i],1000)

#https://docker-py.readthedocs.io/en/stable/containers.html#

client = docker.from_env()
cs=[]	
# remove container with same name
for x in (client.containers.list(all=True)):
	print("rm:",x.name)
	x.remove(force=True)
# create container
for i in range(lenn): 
	name='v'+str(i)
	vicid={"VIC_SHM_ID":str(ids[i])}
	container = client.containers.run('chen116/hb-test',environment=vicid,ipc_mode='host',
		cpu_period=int(1e5),cpu_quota=int(1e5),name=name,detach=True)
	cs.append(container)
	print('running:',name)
	if i<lenn-1:
		time.sleep(20+4*i)
print("shm_docker done")






# sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q)
