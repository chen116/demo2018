
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time

monitoring_items = ["heart_rate","app_mode"]
c = heartbeat.Dom0(monitoring_items,['5','7'])
# c = heartbeat.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()




def res_allo(mode,heart_rate,thread_shared_data,domuid):

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
print(shared_data)
print("Exiting the Monitor, total",threads_cnt,"monitoring threads")
