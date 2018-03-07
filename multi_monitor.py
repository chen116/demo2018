
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time
import pprint
monitoring_items = ["heart_rate","app_mode"]
c = heartbeat.Dom0(monitoring_items,['5'])#,'7'])
# c = heartbeat.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()




def res_allo(anchors,heart_rate,thread_shared_data,domuid):
	if anchors==1:
		print('anchors ACTIVE:')
		cur_b = 0
		myinfo = thread_shared_data[domuid]
		for vcpu in myinfo:
			if vcpu['pcpu']!=-1:
				cur_b=int(vcpu['b'])

		if(heart_rate<30):
			if cur_b<=9900:
				cur_b+=100
				xen_interface.sched_rtds(domuid,10000,cur_b,[])
		if(heart_rate>35):
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
		print('anchors INACTIVE:')
		myinfo = thread_shared_data[domuid]
		cnt=0
		for vcpu in myinfo:
			if vcpu['pcpu']!=-1:
				print('vcpu:',cnt,'b:',vcpu['b'])	
				cnt+=1


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

pp.pprint(shared_data)
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
