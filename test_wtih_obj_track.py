from ctypes import cdll
import ctypes
import sysv_ipc
import sys

import time
import _thread

# for obj track
import numpy as np
import cv2
from tkinter import *
import numpy.fft as fft
shmlib = cdll.LoadLibrary('./shmlib.so')
pids = [1024]

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

vic_win_size = 10;
vic_buf_depth = 1000;
vic_log_file ="vic.log";
vic_min_target = 100;
vic_max_target = 1000;
for i in range(lenn):
	suc = shmlib.anchors_heartbeat_init(pids[i],vic_win_size,vic_buf_depth,vic_log_file,vic_min_target,vic_max_target)
	if suc:
		print("hb_init!")
logmem = []
glomem = []
result = None

# try:
# 	for i in range(lenn):
# 		logmem.append(sysv_ipc.SharedMemory(logids[i]))
# 		glomem.append(sysv_ipc.SharedMemory(gloids[i]))
# 		result=1
# except Exception as e: 
# 	print(e)
# 	print("nooo")
# 	pass



master = Tk()
w1 = Scale(master,from_=0,to=400)
w1.set(100)
w1.pack()
w2 = Scale(master,from_=0,to=400,orient=HORIZONTAL)
w2.set(200)
w2.pack()
cap = cv2.VideoCapture('/root/drop.avi')
ret,frame = cap.read()
frame2 = np.zeros((frame.shape),dtype=frame.dtype)

cnt=-1
while(True):
	cnt+=1
	ret, frame = cap.read()
	try:
		g2 = abs(frame-frame2)
	except:
		break
	cv2.imshow('frame',g2)
	frame2=frame
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	master.update_idletasks()
	master.update()
	for i in range(lenn):
		# p=logmem[i].read()
		shmlib.anchors_heartbeat.restype = ctypes.c_int64
		hbtime = shmlib.anchors_heartbeat(pids[i],cnt)
		hr = shmlib.get_hr_from_hb(pids[i],cnt)/1e6
		print('hbtime',hbtime/1e9,'hr',hr)



	# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
for i in range(lenn):
	if shmlib.anchors_heartbeat_finish(pids[i]):
		print("clean up",pids[i])

 	



