
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time
import pprint
import sys

from pyxs import Client

import apid
with open("info.txt", "w") as myfile:
	myfile.write("")

monitoring_items = ["heart_rate","app_mode","frame_size","timeslice"]

# c = heartbeat.Dom0(monitoring_items,['1','2','3','4'])
monitoring_domU = (sys.argv[3]).split(',')


c = heartbeat.Dom0(monitoring_items,monitoring_domU)

timeslice_us=int(sys.argv[4])
minn=int(timeslice_us*0.01)
default_bw=int(timeslice_us)-minn



class MonitorThread(threading.Thread):
	def __init__(self, threadLock,shared_data,res_allo,domuid,sched,timeslice_us,min_heart_rate,max_heart_rate,keys=['test'],base_path='/local/domain'):
		threading.Thread.__init__(self)
		self.domuid=(domuid)
		self.keys=keys
		self.base_path=base_path
		self.threadLock=threadLock
		self.shared_data=shared_data
		self.res_allo=res_allo
		self.anchors = 2
		self.sched = sched
		self.target_reached_cnt = 0
		self.min_heart_rate=min_heart_rate
		self.max_heart_rate=max_heart_rate
		self.timeslice_us = timeslice_us
		self.mid=(min_heart_rate+max_heart_rate)/2

		self.pid = apid.AdapPID(self.mid,1,min_heart_rate,max_heart_rate)

	def run(self):
		# Acquire lock to synchronize thread
		# self.threadLock.acquire()
		self.vmonitor()
		# Release lock for the next thread
		# self.threadLock.release()
		#print("Exiting " , self.name)
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
							myfile.write(self.domuid+" "+(msg)+ " "+str(time.time())+"\n")
				if self.keys[2] in path.decode():
					self.pid.reset()
					if msg.isdigit():
						with open("info.txt", "a") as myfile:
							myfile.write(self.domuid+" "+(msg)+" frame freq"+ " "+str(time.time())+"\n")
				if self.keys[3] in path.decode():
					self.pid.reset()
					if msg.isdigit():
						tmp_new_timeslice_us = int(msg)*1000
						if self.sched ==1:
							cur_bw = 0
							myinfo = self.shared_data[self.domuid]
							for vcpu in myinfo:
								if vcpu['pcpu']!=-1:
									cur_bw=int(vcpu['b'])
							xen_interface.sched_rtds(self.domuid,tmp_new_timeslice_us,cur_bw/self.timeslice_us*tmp_new_timeslice_us,[])
							xen_interface.sched_rtds(str(int(self.domuid)+2),tmp_new_timeslice_us,(self.timeslice_us-cur_bw)/self.timeslice_us*tmp_new_timeslice_us,[])

							for vcpu in myinfo:
								if vcpu['pcpu']!=-1:
									vcpu['b']=cur_bw/self.timeslice_us*tmp_new_timeslice_us
									vcpu['p']=tmp_new_timeslice_us

						else:
							cur_bw = 0
							myinfo = self.shared_data[self.domuid]
							for vcpu in myinfo:
								if vcpu['pcpu']!=-1:
									cur_bw=int(vcpu['w'])
							xen_interface.sched_credit(self.domuid,cur_bw/self.timeslice_us*tmp_new_timeslice_us)
							xen_interface.sched_credit(str(int(self.domuid)+2),(self.timeslice_us-cur_bw)/self.timeslice_us*tmp_new_timeslice_us)
							for vcpu in myinfo:
								if vcpu['pcpu']!=-1:
									vcpu['w']=cur_bw/self.timeslice_us*tmp_new_timeslice_us
						xen_interface.sched_credit_timeslice(int(msg))
						self.timeslice_us = tmp_new_timeslice_us
						with open("info.txt", "a") as myfile:
							myfile.write(self.domuid+" "+(msg)+" time slice len 6"+ " "+str(time.time())+"\n")							

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
				# 	#print("meow",int(self.domuid),token.decode(),msg)

				self.threadLock.release()

				# #print( token.decode(),':',msg)
	def res_allocat(self,heart_rate):

		minn=int(self.timeslice_us*0.01)


		if int(self.domuid)>=3:
			#print("dummy",int(self.domuid)-2,"heartrate:",heart_rate)
			buf=50
			self.shared_data['cnt'] = (self.shared_data['cnt']+1)%buf
			info = self.domuid+" "+str(heart_rate)+" dummy is here"
			if self.shared_data['cnt']%buf!=0:
				with open("info.txt", "a") as myfile:
					myfile.write(info+"\n")
			else:
				with open("info.txt", "w") as myfile:
					myfile.write(info+"\n")			

			return

		tab='               dom '+str(int(self.domuid))
		if int(self.domuid)<2:
			tab='dom '+str(int(self.domuid))
		#print(tab,'heart_rate',heart_rate)

		cur_bw = 0
		myinfo = self.shared_data[self.domuid]

		if self.sched==1:
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					cur_bw=int(vcpu['b'])
		elif self.sched==0:
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					cur_bw=int(vcpu['w'])

		if self.anchors==3:
			# apid algo
			output = self.pid.update(heart_rate)
			# output+=self.timeslice_us/2
			if self.pid.start>0:
				tmp_cur_bw = output+cur_bw #int(output*cur_bw+cur_bw)-int(output*cur_bw+cur_bw)%100
				if tmp_cur_bw>=self.timeslice_us-minn: #dummy
					cur_bw=self.timeslice_us-minn
				elif tmp_cur_bw<=minn:#self.timeslice_us/3:
					cur_bw=minn#int(self.timeslice_us/3)
				else:
					cur_bw=tmp_cur_bw

			cur_bw=int(cur_bw)#-int(cur_bw)%100

		else:
			self.pid.reset()

		if self.anchors==4:
			# aimd algo
			alpha=3.5
			beta=.9
			free = self.timeslice_us-cur_bw


			# if(heart_rate<self.mid):
			# 	if cur_bw<self.timeslice_us-minn:
			# 		free=free*beta
			# 		cur_bw=self.timeslice_us-free
			# 	else:
			# 		cur_bw=self.timeslice_us-minn
			# if(heart_rate>self.mid):
			# 	if cur_bw>minn:
			# 		free+=alpha*minn
			# 		cur_bw=self.timeslice_us-free


			if(heart_rate<self.min_heart_rate):
				if cur_bw<self.timeslice_us-minn:
					free=free*beta
					cur_bw=self.timeslice_us-free
				else:
					cur_bw=self.timeslice_us-minn
			if(heart_rate>self.max_heart_rate):
				if cur_bw>minn:
					free+=alpha*minn
					cur_bw=self.timeslice_us-free
			cur_bw=int(cur_bw)#-int(cur_bw)%100


		if self.anchors==1:

			alpha=2
			beta=.9
			free = self.timeslice_us-cur_bw

			
			if(heart_rate<self.mid):
				if cur_bw<self.timeslice_us-minn:
					free=free*beta
					cur_bw=self.timeslice_us-free
				else:
					cur_bw=self.timeslice_us-minn
			if(heart_rate>self.mid):
				if cur_bw>minn:
					free+=alpha*minn
					cur_bw=self.timeslice_us-free

			# if(heart_rate<self.mid):
			# 	if cur_bw<self.timeslice_us-2*minn: #dummy
			# 		cur_bw+=minn
			# if(heart_rate>self.mid):
			# 	if cur_bw>minn:
			# 		cur_bw-=minn

			# if(heart_rate<self.min_heart_rate):
			# 	if cur_bw<self.timeslice_us-2*minn: #dummy
			# 		cur_bw+=minn
			# if(heart_rate>self.max_heart_rate):
			# 	if cur_bw>minn:
			# 		cur_bw-=minn
			cur_bw=int(cur_bw)#-int(cur_bw)%100

		if self.anchors==2:
			default_bw=int(self.timeslice_us-minn) #dummy
			if cur_bw!=default_bw:
				cur_bw=default_bw
			cur_bw=int(cur_bw)#-int(cur_bw)%100


		if self.anchors==0:
			default_bw=int(self.timeslice_us/2) #dummy
			if cur_bw!=default_bw:
				cur_bw=default_bw	

		if self.sched==1:
			xen_interface.sched_rtds(self.domuid,self.timeslice_us,cur_bw,[])
			xen_interface.sched_rtds(str(int(self.domuid)+2),self.timeslice_us,self.timeslice_us-cur_bw,[])
			myinfo = self.shared_data[self.domuid]
			cnt=0
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					vcpu['b']=cur_bw
					#print(tab,'vcpu:',cnt,'b:',vcpu['b'])
					cnt+=1	
		elif self.sched==0:
			xen_interface.sched_credit(self.domuid,cur_bw)
			xen_interface.sched_credit(str(int(self.domuid)+2),self.timeslice_us-cur_bw)
			myinfo = self.shared_data[self.domuid]
			cnt=0
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					vcpu['w']=cur_bw
					#print(tab,'vcpu:',cnt,'w:',vcpu['w'])
					cnt+=1	


		buf=10000
		self.shared_data['cnt'] = (self.shared_data['cnt']+1)%buf
		info = self.domuid+" "+str(heart_rate)+" "
		if self.sched==1:
			info += str(self.shared_data[self.domuid][0]['b']/self.timeslice_us) + " "+str(time.time())
		else:
			info += str(self.shared_data[self.domuid][0]['w']/self.timeslice_us) + " "+str(time.time())

		# if self.shared_data['cnt']%buf!=0:
		# 	with open("info.txt", "a") as myfile:
		# 		myfile.write(info+"\n")
		# else:
		# 	with open("info.txt", "w") as myfile:
		#		myfile.write(info+"\n")
		with open("info.txt", "a") as myfile:
			myfile.write(info+"\n")


		return

	# https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
	# cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list






threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()



domuid = '1'
xen_interface.sched_rtds(domuid,timeslice_us,default_bw,[])
xen_interface.sched_rtds(str(int(domuid)+2),timeslice_us,timeslice_us-default_bw,[])
domuid = '2'
xen_interface.sched_credit(domuid,default_bw)
xen_interface.sched_credit(str(int(domuid)+2),timeslice_us-default_bw)


# for i,domuid in enumerate(shared_data['rtxen']):
# 	xen_interface.sched_rtds(domuid,timeslice_us,default_bw,[])
# 	xen_interface.sched_rtds(str(int(domuid)+2),timeslice_us,timeslice_us-default_bw,[])


# for domuid in shared_data['xen']:
# 	xen_interface.sched_credit(domuid,default_bw)
# 	xen_interface.sched_credit(str(int(domuid)+2),timeslice_us-default_bw)

shared_data = xen_interface.get_global_info()



print('monitoring:',monitoring_domU)

min_heart_rate = float(sys.argv[1])
max_heart_rate = float(sys.argv[2])

with open("minmax.txt", "w") as myfile:
	myfile.write("min "+sys.argv[1]+"\n")
	myfile.write("max "+sys.argv[2]+"\n")
	myfile.write("timeslice_us "+str(timeslice_us/1000)+"\n")



	# https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
	# cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list
# https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance

def res_allo():
	return



for domuid in c.domu_ids:
	tmp_thread = MonitorThread(threadLock,shared_data,res_allo,domuid,int(domuid)%2,timeslice_us,min_heart_rate,max_heart_rate, monitoring_items)
	tmp_thread.start()
	threads.append(tmp_thread)




# Wait for all MonitorThreads to complete
threads_cnt=0
for t in threads:
	t.join()
	threads_cnt+=1
#print('FINAL COUNT:',shared_data['cnt'])
pp = pprint.PrettyPrinter(indent=2)
print('Final domUs info:')
shared_data = xen_interface.get_global_info()
default_bw=int(timeslice_us/2)

domuid = '1'
xen_interface.sched_rtds(domuid,timeslice_us,default_bw,[])
xen_interface.sched_rtds(str(int(domuid)+2),timeslice_us,timeslice_us-default_bw,[])
domuid = '2'
xen_interface.sched_credit(domuid,default_bw)
xen_interface.sched_credit(str(int(domuid)+2),timeslice_us-default_bw)

xen_interface.sched_credit_timeslice(timeslice_us/1000)

# for domuid in shared_data['rtxen']:
# 	xen_interface.sched_rtds(domuid,timeslice_us,default_bw,[])
# xen_interface.sched_credit_timeslice(timeslice_us/1000)
# for domuid in shared_data['xen']:
# 	xen_interface.sched_credit(domuid,default_bw)
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
print("Restored RT-Xen, Credit to all domUs have equal cpu time sharing")
