
import subprocess
import heartbeat
import xen_interface

from threading import Thread
import threading
import time

monitoring_items = ["heart_rate","meow"]
c = heartbeat.Dom0(monitoring_items,['1','2'])
# c = heartbeat.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = xen_interface.get_global_info()




def res_allo(heart_rate,thread_shared_data,domuid):
    # https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
    # cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list
    # https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance
    if heart_rate<20:
        if thread_shared_data[domuid]['bud'] < 10000:
            thread_shared_data[domuid]['bud']+=500
            # print('bud',domuid,time.time(),thread_shared_data[domuid]['bud'])
            proc = subprocess.Popen(['xl','sched-rtds','-d',domuid,'-p','10000','-b',str(thread_shared_data[domuid]['bud'])])
            # try:
            #     outs, errs = proc.communicate(timeout=15)
            # except TimeoutExpired:
            #     proc.kill()
            #     outs, errs = proc.communicate()
    if heart_rate>25:
        if thread_shared_data[domuid]['bud'] < 10000:
            thread_shared_data[domuid]['bud']-=100
            # print('bud',time.time(),domuid,thread_shared_data[domuid]['bud'])
            proc = subprocess.Popen(['xl','sched-rtds','-d',domuid,'-p','10000','-b',str(thread_shared_data[domuid]['bud'])])
            # try:
            #     outs, errs = proc.communicate(timeout=15)
            # except TimeoutExpired:
            #     proc.kill()
            #     outs, errs = proc.communicate()
        else:
            print('hey')
    print('bud',domuid,time.time(),thread_shared_data[domuid]['bud'],heart_rate)




for domuid in c.domu_ids:
    tmp_thread = heartbeat.MonitorThread(threadLock,shared_data,res_allo,domuid,monitoring_items)
    tmp_thread.start()
    threads.append(tmp_thread)


# Wait for all MonitorThreads to complete
cntt=0
for t in threads:
    t.join()
    cntt+=1
print("Exiting the Monitor, total",cntt,"threads")
