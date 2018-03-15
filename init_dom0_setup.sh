xl cpupool-cpu-remove Pool-0 11-15
xl cpupool-create name=\"credit\" sched=\"credit\" cpus=["11","12","13","14","14","15"]
xl sched-credit -p credit -s -t 10ms
xl vcpu-pin 0 0 - 0
xl vcpu-pin 0 1 - 1
xl vcpu-pin 0 2 - 2
xl vcpu-pin 0 3 - 3
xl vcpu-pin 0 4 - 4
xl vcpu-pin 1 all 6-10 6-10
xl vcpu-pin 3 all 6-10 6-10
xl cpupool-migrate 2 credit
xl cpupool-migrate 4 credit
xl vcpu-pin 2 all 11-15 11-15
xl vcpu-pin 4 all 11-15 11-15
xl vcpu-list
xl cpupool-list -c
xl cpupool-list
xl sched-credit
xl sched-rtds -v all
xl sched-rtds -d 1 -p 10000 -b 5000
xl sched-rtds -d 3 -p 10000 -b 5000
xl sched-credit -d 2 -w 5000 -c 500
xl sched-credit -d 4 -w 5000 -c 500