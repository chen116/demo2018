
import subprocess
import xencomm

from threading import Thread
import threading


c = xencomm.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = {'vcpu':0,'p':0}


print(subprocess.check_output(['xl', 'list']).decode().split())



def res_allo(heart_rate):
    # https://xenbits.xen.org/docs/unstable/man/xl.1.html#SCHEDULER-SUBCOMMANDS
    # cpupool, vcpupin, rtds-budget,period, extratime
    # https://wiki.xenproject.org/wiki/Tuning_Xen_for_Performance
    # if heart_rate<10
    proc = subprocess.Popen(['xl','list'])
    try:
        outs, errs = proc.communicate(timeout=15)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()





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