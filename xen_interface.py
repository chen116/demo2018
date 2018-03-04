



import subprocess


def set_vcpu(domuid,num_vcpus):
    proc = subprocess.Popen(['xl','vcpu-set',str(domuid),str(num_vcpus)])

def sched_rtds(domuid,p,b,vcpus=[]):
    if vcpus==[]:
        proc = subprocess.Popen(['xl','sched-rtds','-d',str(domuid),'-p',str(p),'-b',str(b)])
    else:
        cmd = ['xl','sched-rtds','-d',str(domuid)]
        for i,vcpu in enumerate(vcpus):
            # proc = subprocess.Popen(['xl','sched-rtds','-d',str(domuid),'-v',str(vcpu),'-p',str(p[i]),'-b',str(b[i])])
            cmd.append('-v')
            cmd.append(str(vcpu))
            cmd.append('-p')
            cmd.append(str(p[i]))
            cmd.append('-b')
            cmd.append(str(b[i]))
        proc = subprocess.Popen(cmd)

def sched_credit(domuid,c,w):
    proc = subprocess.Popen(['xl','sched-credit','-d',str(domuid),'-w',str(w),'-c',str(c)])
