import matplotlib.pyplot as plt 
import sys
import matplotlib


def kk(base_name,figure_cnt):
	

	container_cnt=2

	xs =[]
	ys =[]
	cs =[]
	files=[base_name]

	for i in range(container_cnt):
		xs.append([])
		ys.append([])
		cs.append([])
	#x1,x2,y1,y2=[],[],[],[]
	for i in files:
		filepath = i
		with open(filepath) as fp: 
			for line in fp:  
				its = line.split()
				if len(its)==5:
					if 'bud'==its[0]:
						index = int(its[1])-4
						ts = float(its[2])
						cpu = int(its[3])
						hr = float(its[4])
					xs[index].append(ts)
					ys[index].append(hr)
					cs[index].append(cpu)



	xmin = sys.maxsize
	for x in xs:
		if min(x)<xmin:
			xmin=min(x)

	for i,x in enumerate(xs):
		for j in range(len(x)):
			x[j]-=xmin
	plt.figure(figure_cnt)
	plt.subplot(211)
	opt=[':*b',':*r']
	for i in range(0,len(xs)):
		plt.plot(xs[i],ys[i],opt[i],label=str(i))
	plt.xlabel('time(sec)')
	plt.ylabel('heart rate(frames/sec)')
	plt.title('Simple openCV app')
	plt.legend(('vm1','vm2'))



	plt.subplot(212)
	opt=['-*b','-*r']
	for i in range(0,len(xs)):
		plt.plot(xs[i],cs[i],opt[i])
	plt.xlabel('time(sec)')
	plt.ylabel('budget')
	plt.legend(('vm1','vm2'))
	return 



kk('meow',1)
# kk('vlog0',2)

plt.show()
