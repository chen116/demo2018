

import time



class AdapPID:
	def __init__(self,goal,gamma):
		self.goal=goal
		self.output = 0
		self.gamma = gamma
		self.last_time = 0
		self.psn1=0
		self.isn1=0
		self.isn1sn1=0
		self.ds1=0
		self.dsn1=0
		self.start=0

	def update(self,feedback):

		self.err = self.goal-feedback
		current_time = time.time()
		if self.start==0:
			self.delta_time=0
			self.start=1
		else:
			self.delta_time = current_time - self.last_time



		# if self.start==0:
		# 	self.output = self.p() + self.i()
		# 	self.start=1
		# else:
		self.output = self.p() + self.i() #+ self.p()
		self.last_time = current_time

		return self.output

	def p(self):
		y1=self.err*1
		p = self.gamma * self.err * y1
		self.psn1+=p*self.delta_time
		# print(self.psn1*y1)
		return self.psn1*y1
	def i(self):
		self.isn1+=self.err*self.delta_time
		y2 = self.isn1
		i = self.gamma * self.err * y2
		self.isn1sn1+=i*self.delta_time
		# print(self.isn1sn1*y2)
		return self.isn1sn1*y2
	def d(self):
		self.ds1=self.err/self.delta_time
		y3 = self.ds1
		d = self.gamma * self.err * y3 
		self.dsn1 += d*self.delta_time
		# print(self.dsn1*y3)
		return self.dsn1*y3



# pid = AdapPID(1,0.06)
# time.sleep(0.02)
# feedback = 10

# output = 0

# for i in range(1,1000):
# 	output = pid.update(feedback)
# 	if i<10:
# 		feedback = output
# 	else:
# 		feedback = output
# 	print(feedback)
# 	print(' ')
# 	time.sleep(0.02)
