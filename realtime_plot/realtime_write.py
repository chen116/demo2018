
cnt=0

while True:
	x = input('->')
	if cnt%10!=0:
		with open("test.txt", "a") as myfile:
			myfile.write(x+"\n")
	else:
		with open("test.txt", "w") as myfile:
			myfile.write(x+"\n")
	cnt=(cnt+1)%10