xl vcpu-pin 3 all all all
xl vcpu-pin 2 all all all
xl cpupool-cpu-remove credit 6-14
xl cpupool-cpu-add Pool-0 6-14
xl cpupool-migrate 3 Pool-0
xl cpupool-migrate 2 Pool-0
xl cpupool-cpu-remove credit 15
xl cpupool-cpu-add Pool-0 15
xl vcpu-pin 2 all 6-15 6-15
xl vcpu-pin 3 all 6-15 6-15
xl cpupool-list
xl cpupool-list -c
