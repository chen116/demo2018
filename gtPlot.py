

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
from pandas import DataFrame, Series
import pandas as pd
import pprint
import matplotlib 

matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=30) 
fig = plt.figure(figsize=(16, 9))
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
plt.subplots_adjust(left = 0.13,right=0.84)

maxPoints=5000
inputDataFile="info.txt"


# hypervisorSchedulers=["RT-Xen"]
hypervisorSchedulers=["RT-Xen", "Xen"]
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
font_per = [{'family': 'serif',
        'color':  'k',
        'size': 18,
        },{'family': 'serif',
        'color':  'k',
        # 'weight': 'bold',
        'size': 32,
        }]
ax_improvement_percentage_vs_credit = plt.axes([0.1, 0.91, 0.2, 0.12])
ax_improvement_percentage_vs_credit.text(0.06,0.42,'RT-Xen Advantage:',fontdict=font_per[0])
ax_improvement_percentage_vs_credit_txt = ax_improvement_percentage_vs_credit.text(0.1,0.01,'%.2f%%'%(0),fontdict=font_per[1])
ax_improvement_percentage_vs_credit.axis('off')

ax_improvement_percentage_vs_static = plt.axes([0.65, 0.91, 0.2, 0.12])
ax_improvement_percentage_vs_static.text(0.06,0.42,'RT-Xen Anchors Advantage:',fontdict=font_per[0])
ax_improvement_percentage_vs_static_txt = ax_improvement_percentage_vs_static.text(.5,0.01,'%.2f%%'%(0),fontdict=font_per[1])
ax_improvement_percentage_vs_static.axis('off')

def animate(frame):
    plot_vertlines=True



    # Load new data
    df, mostRecentChanges=loadData(inputDataFile)
    # print df.columns
    # print df.iloc[:,0] # Column
    # print df.iloc[328] # Row

    # Clear out plots
    ax1.clear()
    ax2.clear()
    dummy_colrs = ['cyan','lightgreen']
    dummy_sched=["Free\nResource\n(RT-Xen)","Free\nResource\n(Credit)"]



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
        ax2.plot(
            df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == i+1)]["index"].values,
            100-df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == i+1)]["value2"].values,
            color=dummy_colrs[i],
            lw=((i+1)%2)+3,
            linestyle='--',
            label= dummy_sched[i] )

    # Draw min/max lines
    minmax = open("minmax.txt","r").read()
    minmaxArray = minmax.split('\n')
    min_max = []
    for eachLine in minmaxArray:
        if len(eachLine)>1:
            line = eachLine.split()
            min_max.append(float(line[1]))
    x_for_minmax = []
    miny = []
    maxy = []
    total_x_len = len(df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == 1)]["index"].values)+len(df.loc[(df['type'] == "RECORD_HEARTBEAT") & (df['dom'] == 2)]["index"].values)
    for i in range(total_x_len):
        x_for_minmax.append(i)
        miny.append(min_max[0])
        maxy.append(min_max[1])
    ax1.plot(x_for_minmax,miny,'r')
    ax1.plot(x_for_minmax,maxy,'r',label= 'Target\nFPS\nInterval')

    ax1.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,fontsize=20)
    ax2.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,fontsize=18)


    font = [{'family': 'serif',
            'color':  'dodgerblue',
            'weight': 'bold',
            'size': 15,
            },{'family': 'serif',
            'color':  'forestgreen',
            'weight': 'bold',
            'size': 15,
            }]
    colrs = ['dodgerblue','forestgreen']

    if plot_vertlines:
        # Plot anchors
        for idx, row in df.loc[df['type'] == "RECORD_ANCHORS"].iterrows():
            dom_index=row["dom"]-1
            # print row["index"], row["value"]
            ax1.axvline(x=row["index"],linestyle='-',color=colrs[dom_index])
            ax2.axvline(x=row["index"],linestyle='-',color=colrs[dom_index])
            maxhrs= df.loc[(df['type'] == "RECORD_HEARTBEAT")]["value"].max()
            if row["curMode"]==0:
                ax1.text(row["index"],1.2*maxhrs,"Static 50%",rotation=45,fontdict=font[dom_index])
            elif row["curMode"]==1:
                ax1.text(row["index"],1.2*maxhrs,"Anchors",rotation=45,fontdict=font[dom_index])
            elif row["curMode"]==2:
                ax1.text(row["index"],1.2*maxhrs,"Static 100%",rotation=45,fontdict=font[dom_index])



        # Plot framesize
        for idx, row in df.loc[df['type'] == "RECORD_FRAMESIZE"].iterrows():
            # print row["index"], row["value"]
            dom_index=row["dom"]-1

            ax1.axvline(x=row["index"],linestyle='--',color=colrs[dom_index])
            ax2.axvline(x=row["index"],linestyle='--',color=colrs[dom_index])
            ax2.text(row["index"],25,"frame: "+str(row["curFramesize"]),rotation=45,fontdict=font[dom_index],horizontalalignment='right',verticalalignment='top')



        # Plot timeslice
        for idx, row in df.loc[df['type'] == "RECORD_TIMESLICE"].iterrows():
            # print row["index"], row["value"]
            dom_index=row["dom"]-1

            ax1.axvline(x=row["index"],linestyle=':',color=colrs[dom_index])
            ax2.axvline(x=row["index"],linestyle=':',color=colrs[dom_index])
            ax2.text(row["index"],10,"ts: "+str(row["curTimeslice"]),rotation=45,fontdict=font[dom_index],horizontalalignment='right',verticalalignment='top')


    # print(getAverageAtMode(df, 1, 0))
    # print(getAverageSinceLastChange(df, 1, mostRecentChanges[1]))

    creditMeanSinceLastChange = getAverageSinceLastChange(df, 1, mostRecentChanges[1])
    rtXenMeanSinceLastChange = getAverageSinceLastChange(df, 0, mostRecentChanges[0])

    if (creditMeanSinceLastChange is None) or (rtXenMeanSinceLastChange is None):
        ax_improvement_percentage_vs_credit_txt.set_text('')
    else:
        per=(rtXenMeanSinceLastChange-creditMeanSinceLastChange)/creditMeanSinceLastChange*100
        ax_improvement_percentage_vs_credit_txt.set_text('%.2f%%'%(per))

    rtXenMean50=getAverageAtMode(df, 0, 0)
    rtXenMeanAnchors=getAverageAtMode(df, 0, 1)

    if (rtXenMean50 is None) or (rtXenMeanAnchors is None):
        ax_improvement_percentage_vs_static_txt.set_text('')
    else:
        per=(rtXenMeanAnchors-rtXenMean50)/rtXenMean50*100
        ax_improvement_percentage_vs_static_txt.set_text('%.2f%%'%(per))

    print("%d %d %d %d"%(
        creditMeanSinceLastChange if creditMeanSinceLastChange!= None else 0, 
        rtXenMeanSinceLastChange if rtXenMeanSinceLastChange!= None else 0,
        rtXenMean50 if rtXenMean50!= None else 0,
        rtXenMeanAnchors if rtXenMeanAnchors!= None else 0)
    )

    ax2.set_xlabel('Events',fontsize=15)
    ax1.set_ylabel('Moving Average FPS\n(Window Size = 5)\n(frames/sec)', fontsize=22)
    ax2.set_ylabel('Assigned CPU Time\n(%)', fontsize=22)
    # ax2.set_ylim( 45, 105 )  
    ax2.set_ylim( -5, 105 )



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
    #   for line in inputFile:
    #       pass

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
            # updateCurrentParams(currentParams, "RECORD_ANCHORS", dom-1, splitLine[1])
            pass
        elif lineLength==3:
            debugPrint("Heartbeat update: \n\tdom: %s\n\tHR: %s\n\tCPU: %s"%(
                dom,
                splitLine[1],
                splitLine[2])
            )
            tempRecord=[i, dom, "RECORD_HEARTBEAT", curMode, curFramesize, curTimeslice, splitLine[1], float(splitLine[2])*100]
            pass
        elif lineLength==4:
            debugPrint("Framesize update: \n\tdom: %s\n\tNewFrameSize: %s"%(
                dom,
                splitLine[1])
            )
            tempRecord=[i, dom, "RECORD_FRAMESIZE", curMode, splitLine[1], curTimeslice, splitLine[1]]
            # updateCurrentParams(currentParams, "RECORD_FRAMESIZE", dom-1, splitLine[1])
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
            # updateCurrentParams(currentParams, "RECORD_TIMESLICE", dom-1, splitLine[1])
            pass
        else:
            debugPrint("Unknown size: %d"%(lineLength))
        if anyModeChange(currentParams, dom-1, tempRecord[2], tempRecord[6]):
            updateMostRecentChange(mostRecentChanges, dom-1, i)
        if tempRecord[2]!="RECORD_HEARTBEAT":
            updateCurrentParams(currentParams, tempRecord[2], dom-1, splitLine[1])
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
