
cnt=0
with open("test.txt", "w") as myfile:
	myfile.write("")

while True:
	cnt=(cnt+1)%10
	x = input('->')
	if cnt%10!=0:
		with open("test.txt", "a") as myfile:
			myfile.write(x+"\n")
	else:
		with open("test.txt", "w") as myfile:
			myfile.write(x+"\n")
