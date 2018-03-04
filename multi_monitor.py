
import pprint


import subprocess



import heartbeat


from threading import Thread
import threading
import time


c = heartbeat.Dom0(["heart_rate"],['1'])
# c = heartbeat.Dom0(["heart_rate"])







threadLock = threading.Lock()
threads = []



def create_single_vcpu_info(line):
    single_cpu_info={}
    pcpu = line[3]
    if pcpu.isdigit():
        single_cpu_info['pcpu']=int(pcpu)
    else:
        single_cpu_info['pcpu']=-1
    pcpu_pin = line[6]
    if pcpu_pin.isdigit():
        single_cpu_info['pcpu_pin']=int(pcpu_pin)
    else:
        single_cpu_info['pcpu_pin']=-1    
    return single_cpu_info


shared_data = {}
shared_data['rtxen']=set()
shared_data['xen']=set()

out =  subprocess.check_output(['xl', 'vcpu-list']).decode().split('\n')
out=out[1:-1]
for lines in out:
    line = lines.split()
    if line[1] not in shared_data:
        shared_data[line[1]]={}
        shared_data[line[1]]=[]
        shared_data[line[1]].append(create_single_vcpu_info(line))
    else:
        shared_data[line[1]].append(create_single_vcpu_info(line))


out =  subprocess.check_output(['xl', 'sched-credit']).decode().split('\n')
if out[0]!='':
    out=out[2:-1]
    for lines in out:
        line = lines.split()
        shared_data['xen'].add(line[1])
        for vcpu in shared_data[line[1]]:
            vcpu['w']=int(line[2])
            vcpu['c']=int(line[3])

out =  subprocess.check_output(['xl', 'sched-rtds','-v','all']).decode().split('\n')
if out[0]!='':
    out=out[2:-1]
    for lines in out:
        line = lines.split()
        if line[1]!='0':
            shared_data['rtxen'].add(line[1])
        shared_data[line[1]][int(line[2])]['p']=int(line[3])
        shared_data[line[1]][int(line[2])]['b']=int(line[4])







# for domuid in shared_data:
#     out =  subprocess.check_output(['xl', 'sched-rtds','-d',domuid]).decode().split('\n')
#     out=out[1:-1]
#     for lines in out:
#         line = lines.split()
#         shared_data[line[1]][int(line[2])]['p']=line[3]
#         shared_data[line[1]][int(line[2])]['b']=line[4]


pp = pprint.PrettyPrinter(indent=2)
pp.pprint(shared_data)


# shared_data = {}

# out =  subprocess.check_output(['xl', 'sched-rtds']).decode().split('\n')
# for lines in out:
#     line = lines.split()
#     if line and 'ID' not in line[1] and len(line)==4:
#         shared_data[line[1]]={}
#         shared_data[line[1]]['bud']=int(line[3])
# print(shared_data)



def res_allo(heart_rate,thread_shared_data,domuid):
    print('meow')
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
        print(thread_shared_data[domuid]['bud'] )
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
    tmp_thread = heartbeat.MonitorThread(threadLock,shared_data,res_allo,domuid,["heart_rate"])
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