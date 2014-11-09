#!/usr/bin/env python
"""
by Alex Holcombe
Before brought into the repository, this file was ltrsNoiseAdvanceQuestManually.py
I used to have the noise parameter go from 0 to 1 but with log stepping, staircase always crapped out, don't know why,
so I use percentNoise (0->100) instead of proportion
"""
from __future__ import print_function
from psychopy import core, visual, event, misc, data
import numpy
import numpy as np
from math import atan, log
from copy import deepcopy
import itertools

def numberToLetter(number): #0 = A, 25 = Z
    #if it's not really a letter, return @
    #if type(number) != type(5) and type(number) != type(np.array([3])[0]): #not an integer or numpy.int32
    #    return ('@')
    if number < 0 or number > 25:
        return ('@')
    else: #it's probably a letter
        try:
            return chr( ord('A')+number )
        except:
            return('@')

autoLogging=False
#create a window to draw in
widthPix=600 #monitor width in pixels
monitorwidth = 38.7 #monitor width in cm
viewdist = 57.; #cm
fullscreen = 0

myWin = visual.Window((widthPix,widthPix), allowGUI=False, color=0, 
        monitor='testMonitor',fullscr=fullscreen,winType='pyglet', units='norm')

bgColor = [-1.,-1.,-1.] # [-1,-1,-1]
cueColor = [1.,1.,1.]
letterColor = [1.,1.,1.]
ltrHeight = 2.5
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /numpy.pi*180)

#INITIALISE SOME STIMULI
#predraw all 26 letters 
lettersDrawObjects = list()
for i in range(0,26):
   letterDraw = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
   letterDraw.setHeight( ltrHeight ) #Martini letters were 2.5deg high
   letter = numberToLetter(i)
   #print 'adding letter', letter, ' to the drawing queue'
   letterDraw.setText(letter)
   letterDraw.setColor(bgColor)
   lettersDrawObjects.append(letterDraw)
  
#All noise dot coordinates ultimately in pixels, so can specify each dot is one pixel 
fieldWidthDeg=ltrHeight *1.8
fieldWidthPix = int( round( fieldWidthDeg*pixelperdegree ) )
#create a grid of xy vals
proportnNoise = 0.1

def createNoiseArray(proportnNoise,fieldWidthPix): 
    numDots = int(proportnNoise*fieldWidthPix*fieldWidthPix)
    if numDots ==0:
        return None
    #create a matrix of all possible pixel locations, shuffle it, pick off the first numDots ones
    #0,0 is center of field
    possibleXcoords = -fieldWidthPix/2 + np.arange(fieldWidthPix)
    possibleYcoords = deepcopy(possibleXcoords)
    def expandgrid(*itrs):
       product = list(itertools.product(*itrs))
       return product
    allFieldCoords = expandgrid(possibleXcoords,possibleYcoords)
    #shuffle it
    np.random.shuffle(allFieldCoords)
    dotCoords = allFieldCoords[0:numDots]

    #xys = numpy.random.random([numDots,2])*fieldWidthPix-fieldWidthPix/2.0 #this way yields many dots in the same locations
    #create opacity for each dot
    opacs = numpy.ones(numDots)#all opaque
    verticalAdjust = 3 #number of pixels to raise rectangle by. Using only uppercase letters and seem to be drawn above the line
    horizontalAdjust = 3
    mask = visual.ElementArrayStim(myWin,units='pix', elementTex=None, elementMask=None,
        nElements=numDots, fieldSize=[fieldWidthPix,fieldWidthPix],
        fieldPos=(horizontalAdjust, verticalAdjust),
        colors=-1, #set to black
        xys= dotCoords, 
        opacities=opacs,
        sizes=1)
    return (mask)

noise = createNoiseArray(proportnNoise,fieldWidthPix)

def printStaircaseStuff(staircase, briefTrialUpdate):
    #if briefTrialUpdate, don't print everything, just the kind of stuff you like to know after each trial
    print('staircase.data (incorrect/correct)=',staircase.data)
    if staircase.stepType == 'log':
        print('staircase.intensities (these are log intensities)=[', end='')
        for i in range( len(staircase.intensities) ):
            print('{:.2f} '.format(staircase.intensities[i]), end='') #I cant figure out a simpler way to prevent scientific notation
        print('], exponentiated=[',end='')
        for j in range( len(staircase.intensities) ):
            print('{:.2f} '.format(10**staircase.intensities[j]), end='') #I cant figure out a simpler way to prevent scientific notation
        print(']')
    else: #linear steps, so dont have to worry about log
        print('staircase.intensities =',np.around(staircase.intensities,3))
    if type(staircase) is data.StairHandler:
        numReversals = len(staircase.reversalIntensities)
        print('number of reversals=',  numReversals)
        print('reversal noiseProportions=',1- np.array(staircase.reversalIntensities) )
        if numReversals>0:
            numReverstalsToAvg = numReversals-1
            print('mean of final',numReversalsToAvg,' reversals =',1-np.average(staircase.reversalIntensities[-numReversalsToAvg:]))
    elif type(staircase) is data.QuestHandler:
            #some are private initialization variables I'm not really supposed to access
            if not briefTrialUpdate:
                print('pThreshold (proportion correct for which trying to zero in on the corresponding parameter value) =', staircase._quest.pThreshold)
                print('stopInterval (min 5-95% confidence interval required for  thresh  before stopping. If both this and nTrials is specified, whichever happens first)=',
                            staircase.stopInterval)
                print('stepType=', staircase.stepType)
                print('minVal=', staircase.minVal, 'maxVal=', staircase.maxVal)
                print('nTrials=', staircase.nTrials)
    #below applies to both types of staircase
    if staircase.thisTrialN == -1:
        print('thisTrialN = -1, suggesting you have not started it yet; need to call staircase.next()')
    else:
        print('thisTrialN (current trial number) =',staircase.thisTrialN)
        # staircase.calculateNextIntensity() sounds like something useful to get a preview of the next trial. Instead, seems to be 
        #the internal function used to advance to the next trial.

stepSizesLinear = [.2,.2,.1,.1,.05,.05]
stepSizesLog = [log(1.4,10),log(1.4,10),log(1.3,10),log(1.3,10),log(1.2,10)]
#create the staircase handler
useQuest = True
if  useQuest:
    chrisFajouQuestWorks = data.QuestHandler(startVal = 0.95, startValSd = 0.75,
                          stopInterval=0.3,
                          nTrials=10,
                          #extraInfo = thisInfo,
                          pThreshold = 0.25,    
                          gamma = 1./26,
                          delta=0.02, #lapse rate, I suppose for Weibull function fit
                          method = 'mean',
                          stepType = 'lin',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                          minVal=0.01, maxVal = 1.0
                          )
    staircase = data.QuestHandler(startVal = 95, 
                          startValSd = 100,
                          stopInterval= 1,
                          nTrials=50,
                          #extraInfo = thisInfo,
                          pThreshold = 0.25,    
                          gamma = 1./26,
                          delta=0.02, #lapse rate, I suppose for Weibull function fit
                          method = 'quantile', #uses the median of the posterior as the final answer
                          stepType = 'log',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                          minVal=1, maxVal = 100
                          )
    print('created QUEST staircase')
else: 
    staircase = data.StairHandler(startVal = 0.1,
                              stepType = 'log', #if log, what do I want to multiply it by
                              stepSizes = stepSizesLog,    #step size to use after each reversal
                              minVal=0, maxVal=1,
                              nUp=1, nDown=3,  #will home in on the 80% threshold
                              nReversals = 2, #The staircase terminates when nTrials have been exceeded, or when both nReversals and nTrials have been exceeded
                              nTrials=1)
    print('created conventional staircase')

message =visual.TextStim(myWin,text='NOT YET SET', pos=(0,-0.5))
correctIncorrectMessage = visual.TextStim(myWin,text='', pos=(0,+0.5))

timeForNextTrial = False
refreshNoise=False
thisCorr=2
trialClock = core.Clock()
t=lastFPSupdate=0
expStop= False
nEasyStarterTrials = 0
print('starting staircase with following settings:')
printStaircaseStuff(staircase,False)

doingStaircasePhase = False #First phase of experiment is method of constant stimuli. If use naked QUEST, might converge too soon
initialNonstaircaseTrials = np.array([2, 5, 10, 80]) # np.array([2, 2, 5, 5, 10, 80, 80, 80])#,30, 80, 40, 90, 30, 70, 30, 40, 80, 20, 20, 50 ]

corrEachTrial = list() #only needed for initialNonstaircaseTrials
overallTrialN = -1
while (not staircase.finished) and expStop==False: #staircase.thisTrialN < staircase.nTrials
    if overallTrialN+1 < len(initialNonstaircaseTrials): #still doing initialNonstaircaseTrials
        overallTrialN += 1
        percentNoise = initialNonstaircaseTrials[overallTrialN]
    else:
        if overallTrialN+1 == len(initialNonstaircaseTrials): #add these non-staircase trials so QUEST knows about them
            print('Readying to import ',corrEachTrial,' and intensities ',initialNonstaircaseTrials)
            staircase.importData(100-initialNonstaircaseTrials, np.array(corrEachTrial)) 
        try: #advance the staircase
            percentNoise = 100- staircase.next()  #will step through the staircase, based on whether told it (addData) got it right or wrong
            print('percentNoise for this trial = ',percentNoise) #debugON
            overallTrialN += 1
        except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
            print('stopping because staircase.next() returned a StopIteration, which it is supposed to do when it is finished')
            break #break out of the trials loop
    print('overallTrialN=',overallTrialN)
#    if staircase.thisTrialN < nEasyStarterTrials: #veto staircase recommendation, use very little noise
#            percentNoise = 0.2
    #subtract one because staircase always goes down when you get it right
    thisLetterIdx = np.random.randint(0,26); #choose random letter
    refreshNoise = True
    if timeForNextTrial:
        correctIncorrectMessage.setText( ['WRONG!','RIGHT!'][thisCorr] )
    timeForNextTrial = False
    while not timeForNextTrial:
        message.setText( str(round(percentNoise,2)) )
        message.draw()
        correctIncorrectMessage.draw()
        if refreshNoise:
            noise = createNoiseArray(percentNoise/100.,fieldWidthPix)
            refreshNoise = False
            
        t=trialClock.getTime()
        lettersDrawObjects[thisLetterIdx].setColor( letterColor )
        lettersDrawObjects[thisLetterIdx].draw() #DRAW STIMULUS!
        if noise != None: #more than 0 noise dots
            noise.draw()
        myWin.flip()
        
        #handle key presses each frame
        for key in event.getKeys():
            key = key.upper()
            if key in ['SPACE',]: #a key to press if you want to see a random new noise pattern
                refreshNoise = True
            if key in ['LSHIFT','EQUALS']: #lshift seems to be plus sign, but doesn't work very well
                percentNoise += 2 # min(proportnNoise+0.02,1)
                refreshNoise = True
            if key in ['MINUS']:
                percentNoise += -2 # min(proportnNoise-0.02,1)
                refreshNoise = True
            if key in ['ESCAPE']:
                expStop=True
            if key in ['A','B','C', 'D', 'E','F', 'G','H','I', 'J',  'K', 'L', 'M', 'N', 'O', 'P','Q','R', 'S','T','U','V','W', 'X', 'Y','Z']:
                timeForNextTrial = True
                if ord(key)-ord('A') == thisLetterIdx:
                    thisCorr = 1#correct
                else:
                    thisCorr = 0#incorrect
                corrEachTrial.append(thisCorr)
                if overallTrialN >= len(initialNonstaircaseTrials): #doing staircase trials now
                    staircase.addResponse(thisCorr, intensity = 100-percentNoise) #Add a 1 or 0 to signify a correct/detected or incorrect/missed trial
                    print('Have added an intensity of','{:.3f}'.format(100-percentNoise))
                # an intensity value here indicates that you did not use the recommended intensity in your last trial and the staircase will replace its recorded value with the one you supplied here.
myWin.close()
print('Finished.')
printStaircaseStuff(staircase,True)

if staircase.finished:
    print('Staircase was finished')
else:
    print('Staircase was not finished')
# can now access 1 of 3 suggested threshold levels
#print('staircase mean=',staircase.mean())
#print('staircase mode=',staircase.mode())
print('staircase quantile (median)=','{:.4f}'.format(staircase.quantile()), end='') #gets the median. Prints as floating point with 4 digits of precision
print('. Proportion noise=','{:.4f}'.format(100-staircase.quantile())) 
