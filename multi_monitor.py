
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time
import pprint
monitoring_items = ["heart_rate","app_mode","sched"]
c = heartbeat.Dom0(monitoring_items,['7','8'])
# c = heartbeat.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()




def res_allo(anchors,sched,heart_rate,thread_shared_data,domuid):
	tab='               dom '+str(int(domuid)-6)
	if int(domuid)>7:
		tab='dom '+str(int(domuid)-6)
	print(tab,'heart_rate',heart_rate)

	if sched==1:
		print(tab,"RTDS")
		if len(thread_shared_data['rtxen'])==0:
			while len(thread_shared_data['xen'])>0:
				thread_shared_data['rtxen'].add(thread_shared_data['xen'].pop())
			domuids = thread_shared_data['rtxen']
			xen_interface.set_sched(domuids,1)

	else:
		print(tab,"CREDIT")
		if len(thread_shared_data['xen'])==0:
			xen_interface.set_sched(0)
			while len(thread_shared_data['rtxen'])>0:
				thread_shared_data['xen'].add(thread_shared_data['rtxen'].pop())
			domuids = thread_shared_data['xen']
			xen_interface.set_sched(domuids,0)



	if anchors==1:
		if sched==1:
			print(tab,'RT-Xen anchors ACTIVE:')
			cur_b = 0
			myinfo = thread_shared_data[domuid]
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					cur_b=int(vcpu['b'])

			if(heart_rate<7):
				if cur_b<=9900:
					cur_b+=100
					xen_interface.sched_rtds(domuid,10000,cur_b,[])
			if(heart_rate>15):
				if cur_b>=200:
					cur_b-=100
					xen_interface.sched_rtds(domuid,10000,cur_b,[])
			myinfo = thread_shared_data[domuid]
			cnt=0
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					vcpu['b']=cur_b
					print('vcpu:',cnt,'b:',vcpu['b'])
					cnt+=1
		else:
			print(tab,'Credit anchors ACTIVE:')


	else:
		if sched==1:
			print(tab,'-------------RT-Xen anchors INACTIVE:')
			default_b=4000
			myinfo = thread_shared_data[domuid]
			cnt=0
			not_default_b = 0
			for vcpu in myinfo:
				if vcpu['pcpu']!=-1:
					if vcpu['b']!=default_b:
						not_default_b = 1
						vcpu['b']=default_b

					print(tab,'-------------vcpu:',cnt,'b:',vcpu['b'])	
					cnt+=1
			if not_default_b:
				xen_interface.sched_rtds(domuid,10000,default_b,[])
		else:
			print(tab,'Credit anchors INACTIVE:')





	# xen_interface.update_domu_info(thread_shared_data,domuid)



	return
	# https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
	# cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list
# https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance





for domuid in c.domu_ids:
	tmp_thread = heartbeat.MonitorThread(threadLock,shared_data,res_allo,domuid,monitoring_items)
	tmp_thread.start()
	threads.append(tmp_thread)


# Wait for all MonitorThreads to complete
threads_cnt=0
for t in threads:
	t.join()
	threads_cnt+=1
pp = pprint.PrettyPrinter(indent=2)
shared_data = xen_interface.get_global_info()
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
