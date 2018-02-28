
import subprocess
import xencomm

from threading import Thread
import threading


c = xencomm.Dom0(["heart_rate"])







threadLock = threading.Lock()
threads = []
shared_data = {}

out =  subprocess.check_output(['xl', 'sched-rtds']).decode().split('\n')
for lines in out:
    line = lines.split()
    if line and 'ID' not in line[1] and len(line)==4:
        shared_data[line[1]]={}
        shared_data[line[1]]['bud']=int(line[3])
print(shared_data)



def res_allo(heart_rate,thread_shared_data,domuid):
    # https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
    # cpupool, vcpupin, rtds-budget,period, extratime, vcpu-list
    # https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance

    if heart_rate<200:
        if thread_shared_data[domuid]['bud'] < 10000:
            thread_shared_data[domuid]['bud']+=100
            proc = subprocess.Popen(['xl','sched-rtds','-d',domuid,'-p','10000','-b',str(thread_shared_data[domuid]['bud'])])
            # try:
            #     outs, errs = proc.communicate(timeout=15)
            # except TimeoutExpired:
            #     proc.kill()
            #     outs, errs = proc.communicate()
    if heart_rate>400:
        if thread_shared_data[domuid]['bud'] < 10000:
            thread_shared_data[domuid]['bud']-=100
            proc = subprocess.Popen(['xl','sched-rtds','-d',domuid,'-p','10000','-b',str(thread_shared_data[domuid]['bud'])])
            # try:
            #     outs, errs = proc.communicate(timeout=15)
            # except TimeoutExpired:
            #     proc.kill()
            #     outs, errs = proc.communicate()




for domuid in c.domu_ids:
    tmp_thread = xencomm.MonitorThread(threadLock,shared_data,res_allo,domuid,["heart_rate"])
    tmp_thread.start()
    threads.append(tmp_thread)


# Wait for all threads to complete
for t in threads:
    t.join()
print("Exiting the Monitor")

# Create a queue to communicate with the worker threads
# queue = Queue()


# proc = subprocess.Popen(['xl','list'])#, stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)#,cwd='./linpack')
# try:
#     outs, errs = proc.communicate(timeout=15)
# except TimeoutExpired:
#     proc.kill()
#     outs, errs = proc.communicate()
# st=proc.stdout.read()
# er=proc.stderr.read()