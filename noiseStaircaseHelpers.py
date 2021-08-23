import numpy as np
from psychopy import visual, data, logging
import itertools
from math import log
from copy import deepcopy
from pandas import DataFrame
import pylab, os
from matplotlib.ticker import ScalarFormatter

def toStaircase(x,descendingPsycho):
    #Don't need to take log, staircase internals will do that
    if descendingPsycho:
        y = 100 - np.array(x) #100 because assuming maximum value is 100. E.g. percentNoise is 0 to 100
    else:
        y = np.array(x)
    return y

def outOfStaircase(y,staircase,descendingPsycho):
    #To get inside staircase, it was (100-x)
    #and inside log was taken. So y = log(100-x)
    #So to get x out, it's
    #10**y = 100 - x
    #-x = 10**y - 100
    # x = 100 - 10**y
    if staircase.stepType == 'log': #HOW DO I KNOW IT IS BASE 10? and why doesnt psychopy protect me from log values. I guess actual intensities not meant for user
        x = 10**np.array(y)
    else:
        x = y
    if descendingPsycho:
        x = 100-x

    return x
    
def printStaircase(s, descendingPsycho=False, briefTrialUpdate=False, printInternalVal = False, alsoLog=False):
    #if briefTrialUpdate, don't print everything, just the kind of stuff you like to know after each trial
    #needs logging as a global variable, otherwise will fail when alsoLog=True
    #add is what to add to intensities,
    #mult is what to multiply intensities by,  e.g .if descending psychometric function had to fool QUEST by -1*i + 2
    msg = 'staircase.data (incorrect/correct)=' + str(s.data)
    print(msg)
    if alsoLog:     logging.info(msg)

    if printInternalVal:
        msg = '\tstaircase.intensities, *internal* values [' #(these are log intensities)=['
        for i in range( len(s.intensities) ):
            msg += '{:.2f}, '.format( s.intensities[i] ) #I cant figure out a simpler way to prevent scientific notation
        msg+= ']'
        print(msg)
        if alsoLog:     logging.info(msg)
    msg = '\tstaircase.intensities, values [' 
    for j in range( len(s.intensities) ):
        msg += '{:.2f}, '.format( outOfStaircase(s.intensities[j], s, descendingPsycho) )
    msg+= ']'
    print(msg)
    if alsoLog:     logging.info(msg)

    if type(s) is data.StairHandler:
        numReversals = len(s.reversalIntensities)
        msg= 'staircase number of reversals=' + str(numReversals) + '] '
        msg+= 'reversal noiseProportions=' + str( 1- np.array( outofStaircase(s.reversalIntensities,s,descendingPsycho)) )
        print(msg)
        if alsoLog:     logging.info(msg)
        if numReversals>0:
            numReversalsToAvg = numReversals-1
            msg= ('mean of final' + str(numReversalsToAvg) + 
                      ' reversals =' + str( 1-np.average(  outofStaircase(s.reversalIntensities[-numReversalsToAvg:],s,descendingPsycho),   ) ) )
            print(msg)
            if alsoLog:     logging.info(msg)
    elif type(s) is data.QuestHandler:
            #some of below are private initialization variables I'm not really supposed to access
            if not briefTrialUpdate:
                msg= ('\tpThreshold (proportion correct for which trying to zero in on the corresponding parameter value) =' +
                               str(s._quest.pThreshold) + '\n')
                msg+= ('\tstopInterval (min 5-95% confidence interval required for  thresh  before stopping. If both this and nTrials is specified, whichever happens first)='+
                               str(s.stopInterval) + '\n')
                msg+= '\tstepType=' + str(s.stepType) + '\n'
                msg+= '\tminVal=' + str(s.minVal) + '  maxVal=' + str(s.maxVal) + '\n'
                msg+= '\tnTrials=' + str(s.nTrials)
                print(msg)
                if alsoLog:     logging.info(msg)

    #below applies to both types of staircase
    if s.thisTrialN == -1:
        msg= 'thisTrialN = -1, suggesting you have not started it yet; need to call staircase.next()'
        print(msg)
        if alsoLog:     logging.info(msg)
    else:
        msg= 'staircase thisTrialN =' + str(s.thisTrialN)
        print(msg)
        if alsoLog:     logging.info(msg)
        # staircase.calculateNextIntensity() sounds like something useful to get a preview of the next trial. Instead, seems to be 
        #the internal function used to advance to the next trial.
    
def createNoise(proportnNoise,win,fieldWidthPix,noiseColor): 
    #noiseColor, assumes that colorSpace='rgb', triple between -1 and 1
    #Creates proportnNoise*area dots, in random positions, with color noiseColor (black)
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

def plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshVal):
    #Expects staircase, which has intensities and responses in it
    #May or may not be log steps staircase internals
    #Plotting with linear axes
    #Fit is a psychopy data fit object. Assuming that it couldn't handle descendingPsycho so have to invert the values from it
    intensLinear= outOfStaircase(staircase.intensities, staircase, descendingPsycho)
    if fit is not None:
        #generate psychometric curve
        intensitiesForCurve = pylab.arange(min(intensLinear), max(intensLinear), 0.01)
        thresh = fit.inverse(threshVal)
        if descendingPsycho:
            intensitiesForFit = 100-intensitiesForCurve
            thresh = 100 - thresh
        else:
            intensitiesForFit = intensitiesForCurve
        ysForCurve = fit.eval(intensitiesForFit)
        print('intensitiesForCurve=',intensitiesForCurve)
        #print('ysForCurve=',ysForCurve) #debug
    else: #post-staircase function fitting failed, but can fall back on what staircase returned
        thresh = staircase.quantile()
        if descendingPsycho:
            thresh = 100-thresh
    #plot staircase in left hand panel
    pylab.subplot(121)
    pylab.plot(intensLinear)
    pylab.xlabel("staircase trial")
    pylab.ylabel("% noise")
    #plot psychometric function on the right.
    ax1 = pylab.subplot(122)
    if fit is not None:
        pylab.plot(intensitiesForCurve, ysForCurve, 'k-') #fitted curve
    pylab.plot([thresh, thresh],[0,threshVal],'k--') #vertical dashed line
    pylab.plot([0, thresh],[threshVal,threshVal],'k--') #horizontal dashed line
    figure_title = 'threshold (%.2f) = %0.2f' %(threshVal, thresh) + '%'
    #print thresh proportion top of plot
    pylab.text(0, 1.11, figure_title, horizontalalignment='center', fontsize=12)
    if fit is None:
        pylab.title('Fit failed')
    
    #Use pandas to calculate proportion correct at each level
    df= DataFrame({'intensity': intensLinear, 'response': staircase.data})
    #print('df='); print(df) #debug
    grouped = df.groupby('intensity')
    groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
    intensitiesTested = list(groupMeans.index)
    pCorrect = list(groupMeans['response'])  #x.iloc[:]
    ns = grouped.count() #want n per trial to scale data point size
    ns = list(ns['response'])
    print('df mean at each intensity\n'); print(  DataFrame({'intensity': intensitiesTested, 'pCorr': pCorrect, 'n': ns })   )
    #data point sizes. One entry in array for each datapoint

    pointSizes = 5+ 40 * np.array(ns) / max(ns) #the more trials, the bigger the datapoint size for maximum of 6
    #print('pointSizes = ',pointSizes)
    points = pylab.scatter(intensitiesTested, pCorrect, s=pointSizes, 
        edgecolors=(0,0,0), facecolors= 'none', linewidths=1,
        zorder=10, #make sure the points plot on top of the line
        )
    pylab.ylim([-0.01,1.01])
    pylab.xlim([-2,102])
    pylab.xlabel("%noise")
    pylab.ylabel("proportion correct")
    #save a vector-graphics format for future
    #outputFile = os.path.join(dataFolder, 'last.pdf')
    #pylab.savefig(outputFile)
    createSecondAxis = False
    if createSecondAxis: #presently not used, if fit to log would need this to also show linear scale
        #create second x-axis to show linear percentNoise instead of log
        ax2 = ax1.twiny()
        ax2.set(xlabel='%noise', xlim=[2, 102]) #not quite right but if go to 0, end up with -infinity? and have error
        #ax2.axis.set_major_formatter(ScalarFormatter()) #Show linear labels, not scientific notation
        #ax2 seems to be the wrong object. Why am I using pylab anyway? Matplotlib documentation seems more clear
        #for programming it is recommended that the namespaces be kept separate, http://matplotlib.org/api/pyplot_api.html
        #http://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
        ax2.set_xscale('log')
        ax2.tick_params(axis='x',which='minor',bottom='off')
        
#    #save figure to file
#    outputFile = os.path.join(dataDir, 'test.pdf')
#    pylab.savefig(outputFile)

if __name__ == "__main__":
    #Test staircase functions
    threshCriterion = 0.25
    staircaseTrials = 5
    staircase = data.QuestHandler(startVal = 95, 
                          startValSd = 80,
                          stopInterval= 1, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                          nTrials = staircaseTrials,
                          #extraInfo = thisInfo,
                          pThreshold = threshCriterion, #0.25,    
                          gamma = 1./26,
                          delta=0.02, #lapse rate, I suppose for Weibull function fit
                          method = 'quantile', #uses the median of the posterior as the final answer
                          stepType = 'log',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                          minVal=1, maxVal = 100
                          )
    print('created QUEST staircase')
    
    descendingPsycho = False
    noiseEachTrial = np.array([5,5,5,5,5,5,5,5,5,10,10,10,10,10,10,10,10,10,10,10,20,20,20,20,20,20,20,20,20,20,20,20,50,50,50,50,50,50,50,60,60,60,60,60,60,60,60,60,60,70,70,70,70,70,70,70,80,80,80,80,80,80,80,80,95,95,95,95,95,95,95]) 
    centeredOnZero = noiseEachTrial/100. -0.5
    guessRate = .1  #doesnt work with guessRate=0, fitWeibull doesnt like that
    pCorrEachTrial = guessRate*.5 + (1-guessRate)* 1. / (1. + np.exp(-20*centeredOnZero)) #sigmoidal probability

    print('pCorrEachTrial=',np.around(pCorrEachTrial,2))
    corrEachTrial = np.zeros( len(noiseEachTrial) )
    for i in range( len(noiseEachTrial) ):
        corrEachTrial[i] = np.random.binomial( 1, pCorrEachTrial[i] )
    print('corrEachTrial=',corrEachTrial)
    print('Importing responses ',np.array(corrEachTrial),' and intensities ',noiseEachTrial)
    #Act of importing will cause staircase intensities to log transform because that's how intensities are represented in the staircase
    #staircase internal will be i = log(100-x)
    #-(10**i)-100
    staircase.importData( toStaircase(noiseEachTrial,descendingPsycho), np.array(corrEachTrial) )
    printStaircase(staircase, briefTrialUpdate=False, printInternalVal=True, alsoLog=False)

    #Fit and plot data
    descendingPsycho = False
    fit = None
    intensityForCurveFitting = outOfStaircase(staircase.intensities,staircase,descendingPsycho)
    #print('intensityForCurveFitting=',intensityForCurveFitting)
    if descendingPsycho: 
         intensityForCurveFitting = 100-staircase.intensities #because fitWeibull assumes curve is ascending
    #convert from list of trials to probabilities
    combinedInten, combinedResp, combinedN = \
         data.functionFromStaircase(intensityForCurveFitting, staircase.data, bins='unique')
    print('combinedInten=',combinedInten,'combinedResp=',combinedResp)
    try:
        fit = data.FitWeibull(combinedInten, combinedResp, expectedMin=0, sems = 1.0/len(staircase.intensities))
        print('fit=',fit)
    except:
        print("Fit failed.")
    plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshVal=0.75)
    pylab.show() #must call this to actually show plot

