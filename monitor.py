
import subprocess

proc = subprocess.Popen(['xl','list'])#, stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)#,cwd='./linpack')
print(proc)
try:
	outs, errs = proc.communicate(timeout=15)
except TimeoutExpired:
	proc.kill()
	outs, errs = proc.communicate()
# st=proc.stdout.read()
# er=proc.stderr.read()