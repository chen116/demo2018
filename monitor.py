
import subprocess
import xencomm
from queue import Queue
from threading import Thread
import threading


c = xencomm.Dom0(["heart_rate"])
c.monitor()

# Create a queue to communicate with the worker threads
queue = Queue()


proc = subprocess.Popen(['xl','list'])#, stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)#,cwd='./linpack')
try:
	outs, errs = proc.communicate(timeout=15)
except TimeoutExpired:
	proc.kill()
	outs, errs = proc.communicate()
# st=proc.stdout.read()
# er=proc.stderr.read()