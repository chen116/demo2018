import numpy as np
import matplotlib.pyplot as plt
import sys
aimd_hr_above_min= [95.68, 95.65]
aimd_cpu_use= [31.3, 30.81]


apid_hr_above_min= [94.05, 93.9]
apid_cpu_use= [32.55, 31.87]


static_hr_above_min= [100.0, 100.0]
static_cpu_use= [40.0, 40.0]
s='STATIC'
for i in static_hr_above_min:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='AIMD'
for i in aimd_hr_above_min:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='STPID'
for i in apid_hr_above_min:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')


vm1 = []
vm1.append(static_hr_above_min[0])
vm1.append(aimd_hr_above_min[0])
vm1.append(apid_hr_above_min[0])

vm2 = []
vm2.append(static_hr_above_min[1])
vm2.append(aimd_hr_above_min[1])
vm2.append(apid_hr_above_min[1])

s='STATIC'
for i in static_hr_above_min:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='AIMD'
for i in aimd_hr_above_min:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='APID'
for i in apid_hr_above_min:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')

# exit(0)
ind = np.arange(3)  # the x locations for the groups
width = 0.2  # the width of the bars
patterns = ('*', '+', 'x', '\\', '*', 'o', 'O', '.')

fig, ax = plt.subplots()
rects2 = ax.bar(ind - width*.5, vm1, width*.8,color='blue', label='VM1',hatch='.')
rects3 = ax.bar(ind + width*.5, vm2, width*.8,color='skyblue', label='VM2',hatch='x')

# line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

ax.set_ylabel('Percantage of Heart Rates Meeting Deadline($\\geq$ 10 FPS)',fontsize=12)
ax.set_xticks(ind)
ax.set_xticklabels(('STATIC','AIMD','STPID'),fontsize=12)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=12)
for i in range(3):
	ax.text(ind[i]-.75*width,vm1[i]+15,str(vm1[i])+'%' ,color='k', fontweight='bold',rotation=45,fontsize=12)
	ax.text(ind[i]+0.25*width,vm2[i]+15,str(vm2[i])+'%' ,color='k', fontweight='bold',rotation=45,fontsize=12)
ax.set_ylim([0,120])


labels = [item.get_text() for item in ax.get_yticklabels()]
labels = ['0','20','40','60','80','100','']
ax.set_yticklabels(labels)


fig.savefig('../writing/images/'+ '3vm_fps.pdf', bbox_inches='tight')

plt.show()

# ind = np.arange(2)  # the x locations for the groups
# width = 0.2  # the width of the bars
# patterns = ('*', '+', 'x', '\\', '*', 'o', 'O', '.')




# fig, ax = plt.subplots()
# rects2 = ax.bar(ind - width*1, aimd_hr_above_min, width*.8,color='dodgerblue', label='AIMD',hatch='O')
# rects3 = ax.bar(ind + width*0, apid_hr_above_min, width*.8,color='skyblue', label='APID',hatch='//')
# rects4 = ax.bar(ind + width*1, static_hr_above_min, width*.8, color='darkgrey', label='STATIC',hatch='*')
# line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

# # for i, v in enumerate(ncc):
# #     ax.text(ind  + width*(i-1.1),v, str(v), color='k', fontweight='bold')
# # line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Percantage of FPS $\\geq$ 10')
# # ax.set_title('Scores by group and gender')
# ax.set_xticks(ind)
# ax.set_xticklabels(('VM1','VM2'),fontsize=9)
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),ncol=4, fancybox=True, shadow=False,fontsize=11)

# fig.savefig('../writing/images/'+ '3vm_fps.pdf', bbox_inches='tight')

# plt.show()

