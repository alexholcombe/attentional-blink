import numpy as np
from psychopy import visual, data, logging
import itertools
from math import log
from copy import deepcopy
from pandas import DataFrame
import pylab, os

def printStaircase(staircase, briefTrialUpdate, alsoLog=False):
    #if briefTrialUpdate, don't print everything, just the kind of stuff you like to know after each trial
    #needs logging as a global variable, otherwise will fail when alsoLog=True
    msg = 'staircase.data (incorrect/correct)=' + str(staircase.data)
    print(msg)
    if alsoLog:     logging.info(msg)
    
    if staircase.stepType == 'log':
        msg = '\tstaircase.intensities (these are log intensities)=['
        for i in range( len(staircase.intensities) ):
            msg += '{:.2f} '.format(staircase.intensities[i])
            #print('{:.2f} '.format(staircase.intensities[i]), end='') #I cant figure out a simpler way to prevent scientific notation
        msg+= '], exponentiated=['
        for j in range( len(staircase.intensities) ):
            msg += '{:.2f} '.format(10**staircase.intensities[j])
            #print('{:.2f} '.format(10**staircase.intensities[j]), end='') #I cant figure out a simpler way to prevent scientific notation
        msg+= ']'
        print(msg)
        if alsoLog:     logging.info(msg)
        #print(']')
    else: #linear steps, so dont have to worry about log
        msg = 'staircase.intensities =' + str( np.around(staircase.intensities,3) ) 
        print(msg)
        if alsoLog:     logging.info(msg)
        
    if type(staircase) is data.StairHandler:
        numReversals = len(staircase.reversalIntensities)
        msg= 'staircase number of reversals=' + str(numReversals) + '] '
        msg+= 'reversal noiseProportions=' + str( 1- np.array(staircase.reversalIntensities) )
        print(msg)
        if alsoLog:     logging.info(msg)
        if numReversals>0:
            numReversalsToAvg = numReversals-1
            msg= ('mean of final' + str(numReversalsToAvg) + 
                      ' reversals =' + str( 1-np.average(staircase.reversalIntensities[-numReversalsToAvg:]) ) )
            print(msg)
            if alsoLog:     logging.info(msg)
    elif type(staircase) is data.QuestHandler:
            #some of below are private initialization variables I'm not really supposed to access
            if not briefTrialUpdate:
                msg= ('\tpThreshold (proportion correct for which trying to zero in on the corresponding parameter value) =' +
                               str(staircase._quest.pThreshold) + '\n')
                msg+= ('\tstopInterval (min 5-95% confidence interval required for  thresh  before stopping. If both this and nTrials is specified, whichever happens first)='+
                               str(staircase.stopInterval) + '\n')
                msg+= '\tstepType=' + str(staircase.stepType) + '\n'
                msg+= '\tminVal=' + str(staircase.minVal) + '  maxVal=' + str(staircase.maxVal) + '\n'
                msg+= '\tnTrials=' + str(staircase.nTrials)
                print(msg)
                if alsoLog:     logging.info(msg)

    #below applies to both types of staircase
    if staircase.thisTrialN == -1:
        msg= 'thisTrialN = -1, suggesting you have not started it yet; need to call staircase.next()'
        print(msg)
        if alsoLog:     logging.info(msg)
    else:
        msg= 'staircase thisTrialN =' + str(staircase.thisTrialN)
        print(msg)
        if alsoLog:     logging.info(msg)
        # staircase.calculateNextIntensity() sounds like something useful to get a preview of the next trial. Instead, seems to be 
        #the internal function used to advance to the next trial.
    
def createNoise(proportnNoise,win,fieldWidthPix,noiseColor): 
    #noiseColor, assumes that colorSpace='rgb', triple between -1 and 1
    numDots = int(proportnNoise*fieldWidthPix*fieldWidthPix)
    if numDots ==0:
        return None
    #create a matrix of all possible pixel locations, shuffle it, pick off the first numDots ones
    #0,0 is center of field
    possibleXcoords = -fieldWidthPix/2 + np.arange(fieldWidthPix) 
    possibleXcoords += fieldWidthPix/30 #adding one-tenth because for some mysterious reason not centered, I guess letters aren't drawn centered
    possibleYcoords = deepcopy(possibleXcoords)
    def expandgrid(*itrs):
       product = list(itertools.product(*itrs))
       return product
    allFieldCoords = expandgrid(possibleXcoords,possibleYcoords)
    #shuffle it
    np.random.shuffle(allFieldCoords)
    dotCoords = allFieldCoords[0:numDots]

    #create opacity for each dot
    opacs = np.ones(numDots)#all opaque
    verticalAdjust = 3 #number of pixels to raise rectangle by. Using only uppercase letters and seem to be drawn above the line
    noise = visual.ElementArrayStim(win,units='pix', elementTex=None, elementMask=None,
        nElements=numDots, fieldSize=[fieldWidthPix,fieldWidthPix],
        fieldPos=(0.0, verticalAdjust),
        colorSpace='rgb',
        colors=noiseColor, #set to black
        xys= dotCoords, 
        opacities=opacs,
        sizes=1)
    return (noise,allFieldCoords,numDots) #Can just use noise, but if want to generate new noise of same coherence level quickly, can just shuffle coords

def plotDataAndPsychometricCurve(intensities,responses,fit,threshVal):
    #generate psychometric curve
    smoothInt = pylab.arange(min(intensities), max(intensities), 0.001)
    smoothResp = fit.eval(smoothInt)
    thresh = fit.inverse(threshVal)
    thresh = log(100,10) - thresh #QUEST assumes psychometric function ascending, so had to take 100-intensity
    
    #plot staircase in left hand panel
    pylab.subplot(121)
    pylab.plot(intensities)
    pylab.xlabel("staircase trial")
    pylab.ylabel("log percentNoise")
    #plot psychometric function on the right.
    ax1 = pylab.subplot(122)
    smoothInt = log(100,10) - smoothInt #QUEST assumes psychometric function ascending, so had to take 100-intensity
    pylab.plot(smoothInt, smoothResp, 'k-') #fitted curve
    pylab.plot([thresh, thresh],[0,1],'k--') #vertical dashed line
    pylab.plot([0, thresh],[threshVal,threshVal],'k--') #horizontal dashed line
    figure_title = 'threshold (%.2f) = %0.2f' %(threshVal, thresh)
    #pylab.title(figure_title) #print thresh proportion top of plot
    pylab.text(0, 1.09, figure_title,
             horizontalalignment='center', fontsize=15)
    
    #Use pandas to calculate proportion correct at each level
    df= DataFrame({'intensity': intensities, 'response': responses})
    grouped = df.groupby('intensity')
    groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
    #print('df mean at each intensity\n',  grouped )
    intens = list(groupMeans.index)
    pCorrect = list(groupMeans['response'])  #x.iloc[:]
    intens = log(100,10) - np.array(intens) #QUEST assumes psychometric function ascending, so had to take 100-intensity
    #data point sizes. One entry in array for each datapoint
    ns = grouped.sum() #want n per trial to scale data point size
    ns = list(n['response'])
    pointSizes = np.array(ns) / max(ns) * 6 #the more trials, the bigger the datapoint size for maximum of 6
    points = pylab.scatter(intens, pCorrect, s=pointSizes, 
        edgecolors=(0,0,0), facecolors= 'none', linewidths=1,
        zorder=10, #make sure the points plot on top of the line
        )
    pylab.ylim([-0.01,1.01])
    pylab.xlim([0,2])
    pylab.xlabel("log percentNoise")
    pylab.ylabel("proportion correct")
    #save a vector-graphics format for future
    #outputFile = os.path.join(dataFolder, 'last.pdf')
    #pylab.savefig(outputFile)
    #create second x-axis to show linear percentNoise instead of log
    ax2 = ax1.twiny()
    ax2.set(xlabel='percentNoise', xlim=[0, 100])
#    #save figure to file
#    outputFile = os.path.join(dataDir, 'test.pdf')
#    pylab.savefig(outputFile)
