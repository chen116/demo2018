

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
from pandas import DataFrame, Series
import pandas as pd
import pprint

fig = plt.figure(figsize=(10, 7))
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)

maxPoints=5000
inputDataFile="info.txt"


hypervisorSchedulers=["RT-Xen", "Credit"]
colors = ['blue','limegreen']

DEFAULT_ANCHORSMODE=0
DEFAULT_TIMESLICE=15
DEFAULT_FRAMESIZE=600

# Check for value
# df.loc[df['column_name'] == some_value]
# Check for multiple values
# df.loc[df['column_name'].isin(some_values)]
# Multiple checks
# df.loc[(df['column_name'] == some_value) & df['other_column'].isin(some_values)]

def debugPrint(*args):
	return
	for i in args:
		print('{}'.format(i))
	# print("\n")


def animate(frame):

	# Load new data
	df, mostRecentChanges=loadData(inputDataFile)
	# print df.columns
	# print df.iloc[:,0] # Column
	# print df.iloc[328] # Row

	# Clear out plots
	ax1.clear()
	ax2.clear()

	# Plot main data
	for i, hypervisor in enumerate(hypervisorSchedulers):
		ax1.scatter(
			df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == i+1)]["index"].values,
			df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == i+1)]["value"].values,
			s= ((1)%2)*6+5 , # marker size
			label= hypervisorSchedulers[i],
			color=colors[i])
		ax2.plot(
			df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == i+1)]["index"].values,
			df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == i+1)]["value2"].values,
			color=colors[i],
			lw=((i+1)%2)+3,
			label= hypervisorSchedulers[i] )

	# Draw min/max lines
	# ax1.plot(x_for_minmax,maxy,'r',label= 'Target\nFPS\nInterval')

	# Plot anchors
	for idx, row in df.loc[df['type'] == "RECORD_ANCHORS"].iterrows():
		# print row["index"], row["value"]
		ax1.axvline(x=row["index"])
		ax2.axvline(x=row["index"])


	# Plot framesize
	for idx, row in df.loc[df['type'] == "RECORD_FRAMESIZE"].iterrows():
		# print row["index"], row["value"]
		ax1.axvline(x=row["index"])
		ax2.axvline(x=row["index"])


	# Plot timeslice
	for idx, row in df.loc[df['type'] == "RECORD_TIMESLICE"].iterrows():
		# print row["index"], row["value"]
		ax1.axvline(x=row["index"])
		ax2.axvline(x=row["index"])

	# print(getAverageAtMode(df, 1, 0))
	# print(getAverageSinceLastChange(df, 1, mostRecentChanges[1]))

	creditMeanSinceLastChange = getAverageSinceLastChange(df, 1, mostRecentChanges[1])
	rtXenMeanSinceLastChange = getAverageSinceLastChange(df, 0, mostRecentChanges[0])

	rtXenMean50=getAverageAtMode(df, 0, 0)
	rtXenMeanAnchors=getAverageAtMode(df, 0, 1)

	print("%d %d %d %d"%(
		creditMeanSinceLastChange if creditMeanSinceLastChange!= None else 0, 
		rtXenMeanSinceLastChange if rtXenMeanSinceLastChange!= None else 0,
		rtXenMean50 if rtXenMean50!= None else 0,
		rtXenMeanAnchors if rtXenMeanAnchors!= None else 0)
	)





def getAverageAtMode(df, dom, mode):
	tempFrame=df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == dom+1) & (df['curMode'] == mode)]
	if(len(tempFrame)!=0):
		return tempFrame["value"].mean()
	else:
		return None

def getAverageSinceLastChange(df, dom, cutoff):
	tempFrame=df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == dom+1) & (df['index'] > cutoff)]
	if(len(tempFrame)!=0):
		return tempFrame["value"].mean()
	else:
		return None

def updateMostRecentChange(curMostRecent, dom, newIndex):
	curMostRecent[dom] = newIndex

def anyModeChange(curDict, dom, newParam, newVal):
	if newParam == "RECORD_ANCHORS":
		if curDict[newParam][dom] == newVal:
			return False
		else:
			return True
	elif newParam == "RECORD_HEARTBEAT":
		return False
	elif newParam == "RECORD_FRAMESIZE":
		if curDict[newParam][dom] == newVal:
			return False
		else:
			return True
	elif newParam == "RECORD_TIMESLICE":
		if curDict[newParam][dom] == newVal:
			return False
		else:
			return True

def updateCurrentParams(currentParamDict, param, dom, newParam):
	currentParamDict[param][dom] = newParam

def loadData(fileName):
	# Format: [index, dom, type, curMode, curFramesize, curTimeslice, value{, ...}]
	records=[]
	currentParams={
		"RECORD_ANCHORS": {0:DEFAULT_ANCHORSMODE, 1:DEFAULT_ANCHORSMODE},
		"RECORD_FRAMESIZE": {0:DEFAULT_FRAMESIZE, 1:DEFAULT_FRAMESIZE},
		"RECORD_TIMESLICE": {0:DEFAULT_TIMESLICE, 1:DEFAULT_TIMESLICE}
		}
	mostRecentChanges={}

	# Read whole file into memory
	with open(inputDataFile) as inputFile:
		lines = inputFile.readlines()

	# Read line by line
	# with open(inputDataFile) as inputFile:
	# 	for line in inputFile:
	# 		pass

	# Process lines
	for i, line in enumerate(lines):
		tempRecord=[]
		splitLine=line.split()
		lineLength=len(splitLine)
		debugPrint(i)
		dom=splitLine[0]
		dom = int(dom)
		if (dom-1) not in mostRecentChanges.keys():
			mostRecentChanges[dom-1] = i
		curMode=currentParams["RECORD_ANCHORS"][dom-1]
		curFramesize=currentParams["RECORD_FRAMESIZE"][dom-1]
		curTimeslice=currentParams["RECORD_TIMESLICE"][dom-1]
		if lineLength==2:
			debugPrint("Anchors update: \n\tdom: %s\n\tnewMode: %s"%(
				dom,
				splitLine[1])
			)
			tempRecord=[i, dom, "RECORD_ANCHORS", splitLine[1], curFramesize, curTimeslice, splitLine[1]]
			updateCurrentParams(currentParams, "RECORD_ANCHORS", dom-1, splitLine[1])
			pass
		elif lineLength==3:
			debugPrint("Heartbeat update: \n\tdom: %s\n\tHR: %s\n\tCPU: %s"%(
				dom,
				splitLine[1],
				splitLine[2])
			)
			tempRecord=[i, dom, "RECORD_HEARTBEAT", curMode, curFramesize, curTimeslice, splitLine[1], splitLine[2]]
			pass
		elif lineLength==4:
			debugPrint("Framesize update: \n\tdom: %s\n\tNewFrameSize: %s"%(
				dom,
				splitLine[1])
			)
			tempRecord=[i, dom, "RECORD_FRAMESIZE", curMode, splitLine[1], curTimeslice, splitLine[1]]
			updateCurrentParams(currentParams, "RECORD_FRAMESIZE", dom-1, splitLine[1])
			pass
		elif lineLength==5:
			debugPrint("Unused")
			pass
		elif lineLength==6:
			debugPrint("Timeslice update: \n\tdom: %s\n\tNewTimeSlice: %s"%(
				dom,
				splitLine[1])
			)
			tempRecord=[i, dom, "RECORD_TIMESLICE", curMode, curFramesize, splitLine[1], splitLine[1]]
			updateCurrentParams(currentParams, "RECORD_TIMESLICE", dom-1, splitLine[1])
			pass
		else:
			debugPrint("Unknown size: %d"%(lineLength))
		if anyModeChange(currentParams, dom-1, tempRecord[2], tempRecord[6]):
			updateMostRecentChange(mostRecentChanges, dom-1, i)
		records.append(tempRecord)
		debugPrint(" ")

	# Check size
	print(len(records))
	if len(records) > maxPoints:
		del records[0:len(records)-maxPoints]
	print(len(records))

	records.insert(0,["index", "dom", "type", "curMode", "curFramesize", "curTimeslice", "value", "value2"])

	df = DataFrame(data=records[1:], columns=records[0])
	df[["index"]] = df[["index"]].astype(int)
	df[["dom"]] = df[["dom"]].astype(int)
	df[["type"]] = df[["type"]].astype(str)
	df[["curMode"]] = df[["curMode"]].astype(int)
	df[["curFramesize"]] = df[["curFramesize"]].astype(int)
	df[["curTimeslice"]] = df[["curTimeslice"]].astype(int)
	df[["value"]] = df[["value"]].astype(float)
	df[["value2"]] = df[["value2"]].astype(float)

	# Min index
	minIndex=df.iloc[0]["index"]
	df[["index"]] = df[["index"]]-minIndex
	pprint.pprint(mostRecentChanges)
	for key, value in mostRecentChanges.items():
		mostRecentChanges[key] = value-minIndex


	pprint.pprint(mostRecentChanges)
	pprint.pprint(currentParams)


	return df, mostRecentChanges


def main():
	animate(None)
	ani = animation.FuncAnimation(fig, animate, interval=1000)

	plt.show()

	pass




if __name__ == '__main__':
	main()
