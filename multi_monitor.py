
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time
import pprint
import sys
from pyxs import Client
with open("info.txt", "w") as myfile:
	myfile.write("")

monitoring_items = ["heart_rate","app_mode","frame_size"]
# c = heartbeat.Dom0(monitoring_items,['1','2','3','4'])
c = heartbeat.Dom0(monitoring_items,['1','2'])





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
		maxx=30000
		minn=100

		if int(self.domuid)>=3:
			print("dummy",int(self.domuid)-2,"heartrate:",heart_rate)
			buf=10000
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
					if cur_b<maxx-minn:
						cur_b+=minn
						xen_interface.sched_rtds(self.domuid,maxx,cur_b,[])
						xen_interface.sched_rtds(str(int(self.domuid)+2),maxx,maxx-cur_b,[])
				if(heart_rate>self.max_heart_rate):
					if cur_b>minn:
						cur_b-=minn
						xen_interface.sched_rtds(self.domuid,maxx,cur_b,[])
						xen_interface.sched_rtds(str(int(self.domuid)+2),maxx,maxx-cur_b,[])


				if heart_rate<=self.max_heart_rate and heart_rate >= self.min_heart_rate:
					self.target_reached_cnt+=1
					if self.target_reached_cnt==150:
						self.target_reached_cnt-=15
						if cur_b>minn:
							cur_b-=minn
							xen_interface.sched_rtds(self.domuid,maxx,cur_b,[])
							xen_interface.sched_rtds(str(int(self.domuid)+2),maxx,maxx-cur_b,[])
				else:
					self.target_reached_cnt=0


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
					if cur_w<maxx-minn:
						cur_w+=minn
						xen_interface.sched_credit(self.domuid,cur_w)
						xen_interface.sched_credit(str(int(self.domuid)+2),maxx-cur_w)
				if(heart_rate>self.max_heart_rate):
					if cur_w>minn:
						cur_w-=minn
						xen_interface.sched_credit(self.domuid,cur_w)
						xen_interface.sched_credit(str(int(self.domuid)+2),maxx-cur_w)
				if heart_rate<=self.max_heart_rate and heart_rate >= self.min_heart_rate:
					self.target_reached_cnt+=1
					if self.target_reached_cnt==150:
						self.target_reached_cnt-=15
						if cur_w>minn:
							cur_w-=minn
							xen_interface.sched_credit(self.domuid,cur_w)
							xen_interface.sched_credit(str(int(self.domuid)+2),maxx-cur_w)
				else:
					self.target_reached_cnt=0
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
				default_b=int(maxx/2)
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
					xen_interface.sched_rtds(self.domuid,maxx,default_b,[])
					xen_interface.sched_rtds(str(int(self.domuid)+2),maxx,default_b,[])
			else:
				print(tab,'Credit anchors INACTIVE:')
				default_w=int(maxx/2)
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
	def res_allocat10(self,heart_rate):

		if int(self.domuid)>=3:
			print("dummy",int(self.domuid)-2,"heartrate:",heart_rate)
			buf=10000
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


				if heart_rate<=self.max_heart_rate and heart_rate >= self.min_heart_rate:
					self.target_reached_cnt+=1
					if self.target_reached_cnt==150:
						self.target_reached_cnt-=15
						if cur_b>=200:
							cur_b-=100
							xen_interface.sched_rtds(self.domuid,10000,cur_b,[])
							xen_interface.sched_rtds(str(int(self.domuid)+2),10000,10000-cur_b,[])
				else:
					self.target_reached_cnt=0


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
				if heart_rate<=self.max_heart_rate and heart_rate >= self.min_heart_rate:
					self.target_reached_cnt+=1
					if self.target_reached_cnt==150:
						self.target_reached_cnt-=15
						if cur_w>=200:
							cur_w-=100
							xen_interface.sched_credit(self.domuid,cur_w)
							xen_interface.sched_credit(str(int(self.domuid)+2),10000-cur_w)
				else:
					self.target_reached_cnt=0
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






threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()
maxx=20000
default_bw=int(maxx/2)

for domuid in shared_data['rtxen']:
	xen_interface.sched_rtds(domuid,maxx,default_bw,[])
for domuid in shared_data['xen']:
	xen_interface.sched_credit(domuid,default_bw)
shared_data = xen_interface.get_global_info()





min_heart_rate = float(sys.argv[1])
max_heart_rate = float(sys.argv[2])

with open("minmax.txt", "w") as myfile:
	myfile.write("min "+sys.argv[1]+"\n")
	myfile.write("max "+sys.argv[2]+"\n")


def res_allo(anchors,sched,heart_rate,thread_shared_data,domuid,min_heart_rate,max_heart_rate):
	tab='               dom '+str(int(domuid))
	if int(domuid)<2:
		tab='dom '+str(int(domuid))
	print(tab,'heart_rate',heart_rate)



	if anchors==1:
		if sched==1:
			print(tab,'RT-Xen anchors ACTIVE:')
			cur_b = 0
			myinfo = thread_shared_data[domuid]
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					cur_b=int(vcpu['b'])

			if(heart_rate<min_heart_rate):
				if cur_b<=9800:
					cur_b+=100
					xen_interface.sched_rtds(domuid,10000,cur_b,[])
					xen_interface.sched_rtds(str(int(domuid)+2),10000,10000-cur_b,[])
			if(heart_rate>max_heart_rate):
				if cur_b>=200:
					cur_b-=100
					xen_interface.sched_rtds(domuid,10000,cur_b,[])
					xen_interface.sched_rtds(str(int(domuid)+2),10000,10000-cur_b,[])
			myinfo = thread_shared_data[domuid]
			cnt=0
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					vcpu['b']=cur_b
					print(tab,'vcpu:',cnt,'b:',vcpu['b'])
					cnt+=1
		else:
			print(tab,'Credit anchors ACTIVE:')
			cur_w = 0
			myinfo = thread_shared_data[domuid]
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					cur_w=int(vcpu['w'])

			if(heart_rate<min_heart_rate):
				if cur_w<=9800:
					cur_w+=100
					xen_interface.sched_credit(domuid,cur_w)
					xen_interface.sched_credit(str(int(domuid)+2),10000-cur_w)
			if(heart_rate>max_heart_rate):
				if cur_w>=200:
					cur_w-=100
					xen_interface.sched_credit(domuid,cur_w)
					xen_interface.sched_credit(str(int(domuid)+2),10000-cur_w)
			myinfo = thread_shared_data[domuid]
			cnt=0
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					vcpu['w']=cur_w
					print(tab,'vcpu:',cnt,'w:',vcpu['w'])
					cnt+=1


	else:
		if sched==1:
			print(tab,'-------------RT-Xen anchors INACTIVE:')
			default_b=5000
			myinfo = thread_shared_data[domuid]
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
				xen_interface.sched_rtds(domuid,10000,default_b,[])
				xen_interface.sched_rtds(str(int(domuid)+2),10000,default_b,[])
		else:
			print(tab,'Credit anchors INACTIVE:')
			default_w=5000
			myinfo = thread_shared_data[domuid]
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
				xen_interface.sched_credit(domuid,default_w)
				xen_interface.sched_credit(str(int(domuid)+2),default_w)
	buf=10000
	thread_shared_data['cnt'] = (thread_shared_data['cnt']+1)%buf
	info = domuid+" "+str(heart_rate)+" "
	if sched==1:
		info += str(thread_shared_data[domuid][0]['b'])
	else:
		info += str(thread_shared_data[domuid][0]['w'])


	if thread_shared_data['cnt']%buf!=0:
		with open("info.txt", "a") as myfile:
			myfile.write(info+"\n")
	else:
		with open("info.txt", "w") as myfile:
			myfile.write(info+"\n")



	return
	# https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
	# cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list
# https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance





for domuid in c.domu_ids:
	tmp_thread = MonitorThread(threadLock,shared_data,res_allo,domuid,int(domuid)%2,min_heart_rate,max_heart_rate, monitoring_items)
	tmp_thread.start()
	threads.append(tmp_thread)




# Wait for all MonitorThreads to complete
threads_cnt=0
for t in threads:
	t.join()
	threads_cnt+=1
print('FINAL COUNT:',shared_data['cnt'])
pp = pprint.PrettyPrinter(indent=2)
print('Final domUs info:')
shared_data = xen_interface.get_global_info()
for domuid in shared_data['rtxen']:
	xen_interface.sched_rtds(domuid,maxx,default_bw,[])
for domuid in shared_data['xen']:
	xen_interface.sched_credit(domuid,default_bw)
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
print("Restored RT-Xen, Credit to all domUs have equal cpu time sharing")
