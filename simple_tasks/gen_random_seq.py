import numpy as np


#vm1:
t=0
while t<100:
	man_arrive_at = t+int(np.random.exponential(20,1))
	print(man_arrive_at)
	man_stay_for = int(np.random.exponential(10,1))
	print("man")
	t = man_stay_for + man_arrive_at
	print(t)



print((np.random.exponential(30,2)))
print((np.random.exponential(10,2)))




print((np.random.exponential(60,1)))
print((np.random.exponential(20,1)))
