import heartbeat
import threading
import sys
from pyxs import Client
import time
import numpy as np

with open("info.txt", "w") as myfile:
	myfile.write("")

monitoring_items = ["heart_rate","timeslice"]
comm = heartbeat.DomU(monitoring_items)

comm.write(monitoring_items[1],0)


# a = []
# for i in range(400):
# 	a.append([])
# 	for j in range(400):
# 		a[i].append(j+1)
# a=np.asarray(a)
# b=np.asarray(a)


comm.wait_till_val_read(monitoring_items[1],1)
print("start")


matsize = 500
time_start=time.time()
i=1
while True:
# hb stuff
	a= np.random.rand(matsize, matsize)
	b= np.random.rand(matsize, matsize)	
	c= np.matmul(b,a.T)
	if comm.read(monitoring_items[1])==2:
		break
	with open("info.txt", "a") as myfile:
		myfile.write(str(i)+' '+str(time.time()-time_start)+'\n')
	i+=1
print(time.time()-time_start)