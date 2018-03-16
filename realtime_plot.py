import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
buf = 1000
def animate(i):
    pullData = open("info.txt","r").read()
    dataArray = pullData.split('\n')
    x = []
    hrs = []
    cpus = []
    cnt=[]
    for i in range(2):
        x.append([])
        hrs.append([])
        cpus.append([])
        cnt.append(-1)
        for j in range(buf):
            x[i].append(j)
            hrs[i].append(0)
            cpus[i].append(0)
    for eachLine in dataArray:
        if len(eachLine)>1:
            line = eachLine.split()
            index=int(line[0])-1
            cnt[index]+=1
            hrs[index][cnt[index]]=(float(line[1]))
            cpus[index][cnt[index]]=(float(line[2])/10000)
    for i in range(2):
        hrs[i]=hrs[i][:buf]
        cpus[i]=cpus[i][:buf]

    ax1.clear()
    ax2.clear()
    opts=['r*','b*']
    for i in range(len(x)):
        ax1.plot(x[i],hrs[i],opts[i])
        ax2.plot(x[i],cpus[i],opts[i])

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()


