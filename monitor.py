
import subprocess

proc = subprocess.Popen(['xl','list'], stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)#,cwd='./linpack')


# st=proc.stdout.read()
# er=proc.stderr.read()