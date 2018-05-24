from os import listdir
from os.path import isfile, join
import sys


onlyfiles = [f for f in listdir('./') if isfile(join('./', f))]
# print(onlyfiles)
files = [ f for f in onlyfiles if "mul_" in f]
# if "r" in rand:
#     files = [ f for f in onlyfiles if "mul_" in f]




import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Cursor
from matplotlib.font_manager import FontProperties
from matplotlib.widgets import CheckButtons
import numpy as np
import time
# fig = plt.figure(figsize=(10, 7))
# ax1 = fig.add_subplot(1,1,1)



fcnt=0
color=['r--','g:','k-']
ncd=[]
for f in files:
    x = []
    cyc = []
    pullData = open(f,"r").read()
    dataArray = pullData.split('\n')
    for eachLine in dataArray:
        if len(eachLine)>1:
            line = eachLine.split()
            x.append(float(line[1]))
            cyc.append(int(line[0]))
    ncd.append(cyc[-1])
    # ax1.plot(x,cyc,color[fcnt],label= f)
    # ax1.legend()
    # ax1.set_xlabel('Time(seconds)')
    # ax1.set_ylabel('Number of Computations Completed')
    fcnt+=1


ind = np.arange(1)  # the x locations for the groups
width = 0.05  # the width of the bars
patterns = ('*', '+', 'x', '\\', '*', 'o', 'O', '.')

ncc=[]
ncc.append(ncd[2])
ncc.append(ncd[0])
ncc.append(ncd[1])



fig, ax = plt.subplots()
rects2 = ax.bar(ind - width*1, ncc[0]-10, width*.8,color='darkgrey', label='STATIC',hatch='*')
rects3 = ax.bar(ind + width*0, ncc[1]-10, width*.8,color='teal', label='AIMD',hatch='.')
rects4 = ax.bar(ind + width*1, ncc[2]-10, width*.8, color='turquoise', label='APID',hatch='x')



for i, v in enumerate(ncc):
    ax.text(ind  + width*(i-1.1),v-5, str(v), color='k', fontweight='bold',fontsize=12)
# line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Computation Count',fontsize=12)
# ax.set_title('Scores by group and gender')
ax.set_xticks([ind - width*1,ind - width*0,ind + width*1])
ax.set_xticklabels(['STATIC','AIMD','STPID'],fontsize=12)
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),ncol=4, fancybox=True, shadow=False,fontsize=11)
fig.savefig('../writing/images/'+ 'matmul.pdf', bbox_inches='tight')


plt.show()
