

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
    print('bud',domuid,time.time(),thread_shared_data[domuid]['bud'],heart_rate)