
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time
import pprint
import sys

with open("info.txt", "w") as myfile:
	myfile.write("")

monitoring_items = ["heart_rate","app_mode"]
c = heartbeat.Dom0(monitoring_items,['1','2'])
# c = heartbeat.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()
default_bw=5000
for domuid in shared_data['rtxen']:
	xen_interface.sched_rtds(domuid,10000,default_bw,[])
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






	# if sched==1 and int(domuid)==1:
	# 	print(tab,"RTDS")
	# 	if len(thread_shared_data['rtxen'])==0:
	# 		print(tab,"switiching to RT-Xen")
	# 		while len(thread_shared_data['xen'])>0:
	# 			thread_shared_data['rtxen'].add(thread_shared_data['xen'].pop())
	# 		domuids = thread_shared_data['rtxen']
	# 		# xen_interface.set_sched(domuids,1)

	# elif sched==0 and int(domuid)==1:
	# 	print(tab,"CREDIT")
	# 	if len(thread_shared_data['xen'])==0:
	# 		print(tab,"switiching to CREDIT")
	# 		while len(thread_shared_data['rtxen'])>0:
	# 			thread_shared_data['xen'].add(thread_shared_data['rtxen'].pop())
	# 		domuids = thread_shared_data['xen']
	# 		# xen_interface.set_sched(domuids,0)



	# xen_interface.update_domu_info(thread_shared_data,domuid)



	return
	# https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
	# cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list
# https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance





for domuid in c.domu_ids:
	tmp_thread = heartbeat.MonitorThread(threadLock,shared_data,res_allo,domuid,int(domuid)%2,min_heart_rate,max_heart_rate, monitoring_items)


	tmp_thread.start()
	threads.append(tmp_thread)


# Wait for all MonitorThreads to complete
threads_cnt=0
for t in threads:
	t.join()
	threads_cnt+=1
pp = pprint.PrettyPrinter(indent=2)
print('Final domUs info:')
shared_data = xen_interface.get_global_info()
for domuid in shared_data['rtxen']:
	xen_interface.sched_rtds(domuid,10000,default_bw,[])
for domuid in shared_data['xen']:
	xen_interface.sched_credit(domuid,default_bw)
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
print("Restored RT-Xen, Credit setup for all domUs to equal sharing")
