import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
buf = 1000
def animate(i):
    pullData = open("info.txt","r").read()
    dataArray = pullData.split('\n')
    x = []
    hrs = []
    cpus = []
    for i in range(2):
        x.append([])
        hrs.append([])
        cpus.append([])
        for j in range(buf):
            x[i].append(j)
            hrs[i].append(0)
            cpus[i].append(0)
    cnt=-1
    for eachLine in dataArray:
        cnt+=1
        if len(eachLine)>1:
            line = eachLine.split()
            index=int(line[0])-1
            hrs[index].append(float(line[1]))
            cpus[index].append(float(line[2])/10000)
    for i in range(2):
        hrs[i]=hrs[i][:buf]
        cpus[i]=cpus[i][:buf]

    ax1.clear()
    opts=['r','b']
    for i in range(len(x)):
        ax1.plot(x[i],hrs[i])
        ax1.plot(x[i],cpus[i])
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()


