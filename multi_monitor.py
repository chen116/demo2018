
import subprocess
import xencomm

from threading import Thread
import threading


c = xencomm.Dom0(["heart_rate"])


threadLock = threading.Lock()
threads = []
shared_data = [1]
vic=1

for domuid in c.domu_ids:
    tmp_thread = xencomm.MonitorThread(threadLock,shared_data,domuid,["heart_rate"])
    tmp_thread.start()
    threads.append(tmp_thread)


# Wait for all threads to complete
for t in threads:
    t.join()
print("Exiting the Program!!!")

# Create a queue to communicate with the worker threads
# queue = Queue()


proc = subprocess.Popen(['xl','list'])#, stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)#,cwd='./linpack')
try:
    outs, errs = proc.communicate(timeout=15)
except TimeoutExpired:
    proc.kill()
    outs, errs = proc.communicate()
# st=proc.stdout.read()
# er=proc.stderr.read()