

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.font_manager import FontProperties
import time

fig = plt.figure(figsize=(10, 7))
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
buf = 1000
def animate(i):
    pullData = open("info.txt","r").read()
    minmax = open("minmax.txt","r").read()
    dataArray = pullData.split('\n')
    minmaxArray = minmax.split('\n')


    x = []
    hrs = []
    cpus = []
    anchor_xs = []
    frame_xs = []
    for i in range(2):
        x.append([])
        hrs.append([])
        cpus.append([])
        anchor_xs.append([])
        frame_xs.append([])

        # for j in range(buf):
        #     x[i].append(j)
        #     hrs[i].append(0)
        #     cpus[i].append(0)
    cnt=0
    for eachLine in dataArray:
        if len(eachLine)>1:
            line = eachLine.split()
            index=int(line[0])-1
            if len(line)==3:
                x[index].append(cnt)
                hrs[index].append(float(line[1]))
                cpus[index].append(float(line[2])/10000*100)
            if len(line)==2:
                anchor_xs[index].append(cnt)
            if len(line)==4:
                frame_xs[index].append(cnt)
            cnt+=1
    min_max = []
    for eachLine in minmaxArray:
        if len(eachLine)>1:
            line = eachLine.split()
            min_max.append(float(line[1]))

    ax1.clear()
    ax2.clear()
    sched=["RT-Xen","Credit"]
    colrs = ['blue','orange']
    for i in range(len(x)):
        ax1.scatter(x[i],hrs[i],s= ((i+1)%2)*6+5 ,label= sched[i] ,color=colrs[i])
        ax2.scatter(x[i],cpus[i],s= ((i+1)%2)*6+5,label= sched[i] ,color=colrs[i])
    x_for_minmax = []
    miny = []
    maxy = []
    total_x_len = len(x[0])+len(x[1])
    for i in range(total_x_len):
        x_for_minmax.append(i)
        miny.append(min_max[0])
        maxy.append(min_max[1])
    ax1.plot(x_for_minmax,miny,'r')
    ax1.plot(x_for_minmax,maxy,'r',label= 'Target\nRange')
    fontP = FontProperties()
    fontP.set_size('small')
    ax1.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,prop=fontP)
    # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=3, fancybox=True, shadow=True,prop=fontP)
    # ax2.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),ncol=3, fancybox=True, shadow=True,prop=fontP)
    ax2.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,prop=fontP)
    ax1.set_title('RT-Xen vs Credit Performance \n\n')
    # ax1.set_xlabel('Time\n \n')
    ax2.set_xlabel('Time')
    ax1.set_ylabel('Moving Average FPS(frame_xs/sec) \n (Window Size = 5)')
    ax2.set_ylabel('Assigned CPU Time Percentage (%)')
    ax2.set_ylim( 45, 105 )  
    for i in range(len(anchor_xs)):
        for j in range(len(anchor_xs[i])):
            ax1.axvline(x=anchor_xs[i][j] ,color=colrs[i], linestyle='--')
            ax2.axvline(x=anchor_xs[i][j] ,color=colrs[i], linestyle='--')
            # ax1.text(4, 5, "anchor_xs")
            # ax2.text(4, 5, "anchor_xs")
    for i in range(len(frame_xs)):
        for j in range(len(frame_xs[i])):
            # ax1.text(4, 5, "frame_xs")
            ax1.axvline(x=frame_xs[i][j] ,color=colrs[i], linestyle='-')
            ax2.axvline(x=frame_xs[i][j] ,color=colrs[i], linestyle='-')

            # ax2.text(4, 5, "frame_xs")


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()




# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import time

# fig = plt.figure()
# ax1 = fig.add_subplot(2,1,1)
# ax2 = fig.add_subplot(2,1,2)
# buf = 1000
# def animate(i):
#     pullData = open("info.txt","r").read()
#     dataArray = pullData.split('\n')
#     x = []
#     hrs = []
#     cpus = []
#     cnt=[]
#     for i in range(2):
#         x.append([])
#         hrs.append([])
#         cpus.append([])
#         cnt.append(-1)
#         for j in range(buf):
#             x[i].append(j)
#             hrs[i].append(0)
#             cpus[i].append(0)
#     for eachLine in dataArray:
#         if len(eachLine)>1:
#             line = eachLine.split()
#             index=int(line[0])-1
#             cnt[index]+=1
#             hrs[index][cnt[index]]=(float(line[1]))
#             cpus[index][cnt[index]]=(float(line[2])/10000)
#     for i in range(2):
#         hrs[i]=hrs[i][:buf]
#         cpus[i]=cpus[i][:buf]

#     ax1.clear()
#     ax2.clear()
#     opts=['r*','bo']
#     for i in range(len(x)):
#         ax1.plot(x[i],hrs[i],opts[i],markersize=((i+1)%2)*2+1)
#         ax2.plot(x[i],cpus[i],opts[i],markersize=((i+1)%2)*3+1)

# ani = animation.FuncAnimation(fig, animate, interval=1000)
# plt.show()


