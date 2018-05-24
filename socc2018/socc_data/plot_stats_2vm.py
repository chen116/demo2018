import numpy as np
import matplotlib.pyplot as plt

aimd_inrange_1 = [100.0, 100.0, 54.79, 100.0]
aimd_inrange_2 = [100.0, 95.18, 54.17, 100.0]

aimd_cpu_1 = [40.08, 39.5, 39.5, 41.6]
aimd_cpu_2 = [39.88, 45.01, 60.3, 58.26]


apid_inrange_1 = [96.43, 81.13, 77.63, 89.61]
apid_inrange_2 = [98.21, 95.0, 50.82, 94.44]

apid_cpu_1 = [42.17, 40.26, 36.31, 41.28]
apid_cpu_2 = [43.06, 48.62, 58.95, 59.58]


static_inrange_1 = [100.0, 100.0, 0.0, 0.0]
static_inrange_2 = [100.0, 0.0, 0.0, 100.0]

static_cpu_1 = [50.0, 50.0, 50.0, 50.0]
static_cpu_2 = [50.0, 50.0, 50.0, 50.0]








s='STATIC'
for i in static_inrange_1:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='AIMD'
for i in aimd_inrange_1:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='APID'
for i in apid_inrange_1:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')

print('')
s='STATIC'
for i in static_inrange_2:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='AIMD'
for i in aimd_inrange_2:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')
s='APID'
for i in apid_inrange_2:
	s+=('& '+str(i)+'\\% ')
print(s+ ' \\\\ \\hline')




##

for jj in range(4):
	vm1=[static_inrange_1[jj],aimd_inrange_1[jj],apid_inrange_1[jj]]
	vm2=[static_inrange_2[jj],aimd_inrange_2[jj],apid_inrange_2[jj]]

	ind = np.arange(3)  # the x locations for the groups
	width = 0.3  # the width of the bars
	patterns = ('*', '+', 'x', '\\', '*', 'o', 'O', '.')
	fig, ax = plt.subplots(figsize=(8, 6))
	rects2 = ax.bar(ind - width*0.5, vm1, width*.8,color='blue', label='VM1',hatch='.')
	rects4 = ax.bar(ind + width*0.5, vm2, width*.8, color='skyblue', label='VM2',hatch='x')
	# line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')
	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Percantage of Heart Rates Meeting Deadline($\\geq$ 10 FPS)',fontsize=14)
	# ax.set_title('Scores by group and gender')
	ax.set_xticks(ind)
	ax.set_xticklabels(('STATIC','AIMD','STPID'),fontsize=16)
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=14)
	for i in range(3):
		ax.text(ind[i]- width*0.8,vm1[i]+12.5,str(vm1[i])+'%' ,color='k', fontweight='bold',rotation=45,fontsize=12)
		ax.text(ind[i]+ width*0.2,vm2[i]+12.5,str(vm2[i])+'%' ,color='k', fontweight='bold',rotation=45,fontsize=12)
	ax.set_ylim([0,120])

	labels = [item.get_text() for item in ax.get_yticklabels()]
	labels = ['0','20','40','60','80','100','']
	ax.set_yticklabels(labels)
	fig.savefig('../writing/images/'+ '2vm_r'+str(jj+1)+'.pdf', bbox_inches='tight')






# plt.show()

if False:
	fig, ax = plt.subplots(figsize=(8, 6))

	rects2 = ax.bar(ind - width*0.5, aimd_inrange_1, width*.8,color='blue', label='VM1',hatch='.')
	rects4 = ax.bar(ind + width*0.5, aimd_inrange_2, width*.8, color='skyblue', label='VM2',hatch='x')
	# line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')


	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Percantage of Heart Rates $\\geq$ 10 FPS',fontsize=12)
	# ax.set_title('Scores by group and gender')
	ax.set_xticks(ind)
	ax.set_xticklabels(('0~30 seconds\nVM1:Medium Workload\nVM2:Medium Workload', '30~60 seconds\nVM1:Medium Workload\nVM2:Heavy Workload', '60~90 seconds\nVM1:Heavy Workload\nVM2:Heavy Workload','90~120 seconds\nVM1:Heavy Workload\nVM2:Medium Workload'),fontsize=9)

	ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=12)
	for i in range(4):
		ax.text(ind[i]- width*0.9,aimd_inrange_1[i]+12.5,str(aimd_inrange_1[i])+'%' ,color='k', fontweight='bold',rotation=45)
		ax.text(ind[i]+ width*0.2,aimd_inrange_2[i]+12.5,str(aimd_inrange_2[i])+'%' ,color='k', fontweight='bold',rotation=45)
	ax.set_ylim([0,120])

	labels = [item.get_text() for item in ax.get_yticklabels()]
	labels = ['0','20','40','60','80','100','']
	ax.set_yticklabels(labels)
	fig.savefig('../writing/images/'+ '2vm_fps_aimd.pdf', bbox_inches='tight')


	fig, ax = plt.subplots(figsize=(8, 6))

	rects2 = ax.bar(ind - width*0.5, apid_inrange_1, width*.8,color='blue', label='VM1',hatch='.')
	rects4 = ax.bar(ind + width*0.5, apid_inrange_2, width*.8, color='skyblue', label='VM2',hatch='x')
	# line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Percantage of FPS $\\geq$ 10',fontsize=12)
	# ax.set_title('Scores by group and gender')
	ax.set_xticks(ind)
	ax.set_xticklabels(('0~30 seconds\nVM1:Medium Workload\nVM2:Medium Workload', '30~60 seconds\nVM1:Medium Workload\nVM2:Heavy Workload', '60~90 seconds\nVM1:Heavy Workload\nVM2:Heavy Workload','90~120 seconds\nVM1:Heavy Workload\nVM2:Medium Workload'),fontsize=9)
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=12)
	for i in range(4):
		ax.text(ind[i]- width*1,apid_inrange_1[i]+12.5,str(apid_inrange_1[i])+'%' ,color='k', fontweight='bold',rotation=45)
		ax.text(ind[i]+ width*0.2,apid_inrange_2[i]+12.5,str(apid_inrange_2[i])+'%' ,color='k', fontweight='bold',rotation=45)
	ax.set_ylim([0,120])

	labels = [item.get_text() for item in ax.get_yticklabels()]
	labels = ['0','20','40','60','80','100','']
	ax.set_yticklabels(labels)
	fig.savefig('../writing/images/'+ '2vm_fps_apid.pdf', bbox_inches='tight')


	plt.show()
	# exit(0)



# ind = np.arange(4)  # the x locations for the groups
# width = 0.2  # the width of the bars
# patterns = ('*', '+', 'x', '\\', '*', 'o', 'O', '.')
# fig, ax = plt.subplots(figsize=(8, 6))
# rects2 = ax.bar(ind - width*0.5, static_inrange_1, width*.8,color='blue', label='VM1',hatch='.')
# rects4 = ax.bar(ind + width*0.5, static_inrange_2, width*.8, color='skyblue', label='VM2',hatch='x')
# # line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Percantage of FPS $\\geq$ 10',fontsize=12)
# # ax.set_title('Scores by group and gender')
# ax.set_xticks(ind)
# ax.set_xticklabels(('0~30 seconds\nVM1:Medium Workload\nVM2:Medium Workload', '30~60 seconds\nVM1:Medium Workload\nVM2:Heavy Workload', '60~90 seconds\nVM1:Heavy Workload\nVM2:Heavy Workload','90~120 seconds\nVM1:Heavy Workload\nVM2:Medium Workload'),fontsize=9)

# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=12)



# for i in range(4):
# 	ax.text(ind[i]- width*0.9,static_inrange_1[i]+12.5,str(static_inrange_1[i])+'%' ,color='k', fontweight='bold',rotation=45)
# 	ax.text(ind[i]+ width*0.2,static_inrange_2[i]+12.5,str(static_inrange_2[i])+'%' ,color='k', fontweight='bold',rotation=45)
# ax.set_ylim([0,120])

# labels = [item.get_text() for item in ax.get_yticklabels()]
# labels = ['0','20','40','60','80','100','']
# ax.set_yticklabels(labels)


# fig.savefig('../writing/images/'+ '2vm_fps_static.pdf', bbox_inches='tight')



# fig, ax = plt.subplots(figsize=(8, 6))

# rects2 = ax.bar(ind - width*0.5, aimd_inrange_1, width*.8,color='blue', label='VM1',hatch='.')
# rects4 = ax.bar(ind + width*0.5, aimd_inrange_2, width*.8, color='skyblue', label='VM2',hatch='x')
# # line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')


# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Percantage of FPS $\\geq$ 10',fontsize=12)
# # ax.set_title('Scores by group and gender')
# ax.set_xticks(ind)
# ax.set_xticklabels(('0~30 seconds\nVM1:Medium Workload\nVM2:Medium Workload', '30~60 seconds\nVM1:Medium Workload\nVM2:Heavy Workload', '60~90 seconds\nVM1:Heavy Workload\nVM2:Heavy Workload','90~120 seconds\nVM1:Heavy Workload\nVM2:Medium Workload'),fontsize=9)

# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=12)
# for i in range(4):
# 	ax.text(ind[i]- width*0.9,aimd_inrange_1[i]+12.5,str(aimd_inrange_1[i])+'%' ,color='k', fontweight='bold',rotation=45)
# 	ax.text(ind[i]+ width*0.2,aimd_inrange_2[i]+12.5,str(aimd_inrange_2[i])+'%' ,color='k', fontweight='bold',rotation=45)
# ax.set_ylim([0,120])

# labels = [item.get_text() for item in ax.get_yticklabels()]
# labels = ['0','20','40','60','80','100','']
# ax.set_yticklabels(labels)
# fig.savefig('../writing/images/'+ '2vm_fps_aimd.pdf', bbox_inches='tight')


# fig, ax = plt.subplots(figsize=(8, 6))

# rects2 = ax.bar(ind - width*0.5, apid_inrange_1, width*.8,color='blue', label='VM1',hatch='.')
# rects4 = ax.bar(ind + width*0.5, apid_inrange_2, width*.8, color='skyblue', label='VM2',hatch='x')
# # line = ax.plot([ind[0] - width*1.5,ind[-1] + width*1.5],[100,100],'k')

# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Percantage of FPS $\\geq$ 10',fontsize=12)
# # ax.set_title('Scores by group and gender')
# ax.set_xticks(ind)
# ax.set_xticklabels(('0~30 seconds\nVM1:Medium Workload\nVM2:Medium Workload', '30~60 seconds\nVM1:Medium Workload\nVM2:Heavy Workload', '60~90 seconds\nVM1:Heavy Workload\nVM2:Heavy Workload','90~120 seconds\nVM1:Heavy Workload\nVM2:Medium Workload'),fontsize=9)
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=4, fancybox=True, shadow=False,fontsize=12)
# for i in range(4):
# 	ax.text(ind[i]- width*1,apid_inrange_1[i]+12.5,str(apid_inrange_1[i])+'%' ,color='k', fontweight='bold',rotation=45)
# 	ax.text(ind[i]+ width*0.2,apid_inrange_2[i]+12.5,str(apid_inrange_2[i])+'%' ,color='k', fontweight='bold',rotation=45)
# ax.set_ylim([0,120])

# labels = [item.get_text() for item in ax.get_yticklabels()]
# labels = ['0','20','40','60','80','100','']
# ax.set_yticklabels(labels)
# fig.savefig('../writing/images/'+ '2vm_fps_apid.pdf', bbox_inches='tight')


plt.show()



