import matplotlib.pyplot as plt 
import sys
import matplotlib


def kk(base_name,figure_cnt):
	

	container_cnt=1

	xs =[]
	ys =[]
	cs =[]
	files=[base_name]

	for i in range(container_cnt):
		xs.append([])
		ys.append([])
		cs.append([])
	#x1,x2,y1,y2=[],[],[],[]
	index=0
	for i in files:
		filepath = i
		with open(filepath) as fp: 
			for line in fp:  
				its = line.split()
				if len(its)==4:
					hr = float(its[3])
					ts = float(its[1])
					xs[index].append(ts)
					ys[index].append(hr)
				if len(its)>8:
					index = int(its[1])
					cpu = int(its[-1])/1e4
					hr = float(its[7])
					ts = int(its[5])
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
			x[j]=x[j]
	plt.figure(figure_cnt)
	# plt.subplot(211)
	opt=[':*b',':*r']
	for i in range(0,len(xs)):
		plt.plot(xs[i],ys[i],opt[i],label=str(i))
	plt.xlabel('time(sec)')
	plt.ylabel('heart rate(frames/sec)')
	plt.title('Demo openCV app on DomU')
	# plt.legend(('frames/sec'))



	# plt.subplot(212)
	# opt=['-*b','-*r']
	# for i in range(0,len(xs)):
	# 	plt.plot(xs[i],cs[i],opt[i])
	# plt.xlabel('time(sec)')
	# plt.ylabel('CPUs')
	# plt.legend(('c0','c1'))
	# return 



kk('logtest',1)
# kk('vlog0',2)

plt.show()
