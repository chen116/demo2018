xl vcpu-pin 3 all all all
xl vcpu-pin 2 all all all
xl cpupool-cpu-remove Pool-0 6-15
xl cpupool-cpu-add credit 6-15
xl cpupool-migrate 3 credit
xl cpupool-migrate 2 credit
xl vcpu-pin 2 all 6-15 6-15
xl vcpu-pin 3 all 6-15 6-15
xl cpupool-list
xl cpupool-list -c
