

import pprint


import subprocess


def update_domu_info(shared_data, domuid):
    def update_single_vcpu_info(line):
        single_cpu_info={}
        pcpu = line[3]
        if pcpu.isdigit():
            single_cpu_info['pcpu']=int(pcpu)
        else:
            single_cpu_info['pcpu']=-1
        pcpu_pin = line[6]
        single_cpu_info['pcpu_pin']=pcpu_pin   
        return single_cpu_info

    out =  subprocess.check_output(['xl', 'vcpu-list',domuid]).decode().split('\n')
    out=out[1:-1]
    cnt=0
    for lines in out:
        line = lines.split()
        shared_data[domuid][cnt]=update_single_vcpu_info(line)
        cnt+=1

    if domuid in shared_data['xen']:
        out =  subprocess.check_output(['xl', 'sched-credit','-d',domuid]).decode().split('\n')
        out=out[2:-1]
        for lines in out:
            line = lines.split()
            for vcpu in shared_data[domuid]:
                vcpu['w']=int(line[2])
                vcpu['c']=int(line[3])
    else:
        out =  subprocess.check_output(['xl', 'sched-rtds','-d',domuid,'all']).decode().split('\n')
        out=out[1:-1]

        for lines in out:
            line = lines.split()
            shared_data[domuid][int(line[2])]['p']=int(line[3])
            shared_data[domuid][int(line[2])]['b']=int(line[4])   



def get_global_info():
    def create_single_vcpu_info(line):
        single_cpu_info={}
        pcpu = line[3]
        if pcpu.isdigit():
            single_cpu_info['pcpu']=int(pcpu)
        else:
            single_cpu_info['pcpu']=-1
        pcpu_pin = line[6]
        single_cpu_info['pcpu_pin']=pcpu_pin
        # if pcpu_pin.isdigit():
        #     single_cpu_info['pcpu_pin']=int(pcpu_pin)
        # else:
        #     single_cpu_info['pcpu_pin']=-1    
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





    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(shared_data)
    return shared_data

def set_vcpu(domuid,num_vcpus):
    proc = subprocess.Popen(['xl','vcpu-set',str(domuid),str(num_vcpus)])

def set_sched(domuids,sched):
    if sched==0: # switching to credit
        for domuid in domuids:
            tmp_cmd=['xl','vcpu-pin',domuid,'all','all','all']
            proc = subprocess.Popen(tmp_cmd)
            proc.wait()
        tmp_cmd = ['xl', 'cpupool-cpu-remove', 'Pool-0', '6-15']
        proc = subprocess.Popen(tmp_cmd)
        proc.wait()
        tmp_cmd = ['xl', 'cpupool-cpu-add', 'credit', '6-15']
        proc = subprocess.Popen(tmp_cmd)
        proc.wait()        
        for domuid in domuids:
            tmp_cmd=['xl','cpupool-migrate',domuid,'credit']
            proc = subprocess.Popen(tmp_cmd)
            proc.wait()   
        for domuid in domuids:
            tmp_cmd=['xl','vcpu-pin',domuid,'all','6-15','6-15']
            proc = subprocess.Popen(tmp_cmd)
            proc.wait()   
        # cmd=[]
        # for domuid in domuids:
        #     tmp_cmd=['xl','vcpu-pin',domuid,'all','all','all','&&']
        #     for tmp in tmp_cmd:
        #         cmd.append(tmp)
        # tmp_cmd = ['xl', 'cpupool-cpu-remove', 'Pool-0', '6-15','&&']
        # for tmp in tmp_cmd:
        #     cmd.append(tmp)
        # tmp_cmd = ['xl', 'cpupool-cpu-add', 'credit', '6-15','&&']
        # for tmp in tmp_cmd:
        #     cmd.append(tmp)
        # for domuid in domuids:
        #     tmp_cmd=['xl','cpupool-migrate',domuid,'credit','&&']
        #     for tmp in tmp_cmd:
        #         cmd.append(tmp)
        # for domuid in domuids:
        #     tmp_cmd=['xl','vcpu-pin',domuid,'all','6-15','6-15','&&']
        #     for tmp in tmp_cmd:
        #         cmd.append(tmp)
        # cmd=cmd[:-1]
        # print(cmd)
        # proc = subprocess.Popen(cmd, shell=True)
    else:
        for domuid in domuids:
            tmp_cmd=['xl','vcpu-pin',domuid,'all','all','all']
            proc = subprocess.Popen(tmp_cmd)
            proc.wait()
        for domuid in domuids:
            tmp_cmd=['xl','cpupool-migrate',domuid,'Pool-0']
            proc = subprocess.Popen(tmp_cmd)
            proc.wait()
        tmp_cmd = ['xl', 'cpupool-cpu-remove', 'credit', '6-15']
        proc = subprocess.Popen(tmp_cmd)
        proc.wait()
        tmp_cmd = ['xl', 'cpupool-cpu-add', 'Pool-0', '6-15']
        proc = subprocess.Popen(tmp_cmd)
        proc.wait()
        for domuid in domuids:
            tmp_cmd=['xl','vcpu-pin',domuid,'all','6-15','6-15']
            proc = subprocess.Popen(tmp_cmd)
            proc.wait()
        # cmd=[]
        # for domuid in domuids:
        #     tmp_cmd=['xl','vcpu-pin',domuid,'all','all','all','&&']
        #     for tmp in tmp_cmd:
        #         cmd.append(tmp)
        # for domuid in domuids:
        #     tmp_cmd=['xl','cpupool-migrate',domuid,'Pool-0','&&']
        #     for tmp in tmp_cmd:
        #         cmd.append(tmp)
        # tmp_cmd = ['xl', 'cpupool-cpu-remove', 'credit', '6-15','&&']
        # for tmp in tmp_cmd:
        #     cmd.append(tmp)
        # tmp_cmd = ['xl', 'cpupool-cpu-add', 'Pool-0', '6-15','&&']
        # for tmp in tmp_cmd:
        #     cmd.append(tmp)
        # for domuid in domuids:
        #     tmp_cmd=['xl','vcpu-pin',domuid,'all','6-15','6-15','&&']
        #     for tmp in tmp_cmd:
        #         cmd.append(tmp)
        # cmd=cmd[:-1]
        # proc = subprocess.Popen(cmd, shell=True)





def sched_rtds(domuid,p,b,vcpus):
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
