#!/usr/bin/env python
"""
by Alex Holcombe
Before brought into the repository, this file was ltrsNoiseAdvanceQuestManually.py
I used to have the noise parameter go from 0 to 1 but with log stepping, staircase always crapped out, don't know why,
so I use percentNoise (0->100) instead of proportion
"""
from __future__ import print_function
from psychopy import core, visual, event, misc, data
import numpy as np
import os, pylab
from math import atan, log
from noiseStaircaseHelpers import printStaircase, createNoise, plotDataAndPsychometricCurve

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
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)

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

(noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,fieldWidthPix,bgColor)

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
printStaircase(staircase, briefTrialUpdate=True, add=2, mult=-1, alsoLog=False)

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
            overallTrialN += 1
        except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
            print('stopping because staircase.next() returned a StopIteration, which it is supposed to do when it is finished')
            break #break out of the trials loop
    print('overallTrialN=',overallTrialN, '   percentNoise for this trial = ', round(percentNoise,2)) #debugON

    thisLetterIdx = np.random.randint(0,26); #choose random letter
    refreshNoise = True
    if timeForNextTrial:
        correctIncorrectMessage.setText( ['WRONG!','RIGHT!'][thisCorr] )
    timeForNextTrial = False
    while not timeForNextTrial:
        message.setText( 'Noise = ' + str(round(percentNoise,2)) + '%' )
        message.draw()
        correctIncorrectMessage.draw()
        if refreshNoise:
            (noise,allFieldCoords,numNoiseDots) = createNoise(percentNoise/100.,myWin,fieldWidthPix,bgColor)
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
printStaircase(staircase, briefTrialUpdate=True, add=2, mult=-1, alsoLog=False)

if staircase.finished:
    print('Staircase was finished')
else:
    print('Staircase was not finished')
# can now access 1 of 3 suggested threshold levels
#print('staircase mean=',staircase.mean())
#print('staircase mode=',staircase.mode())
print('staircase quantile (median)=','{:.4f}'.format(staircase.quantile()), end='') #gets the median. Prints as floating point with 4 digits of precision
print('. Proportion noise=','{:.4f}'.format(100-staircase.quantile())) 


intensities = staircase.intensities
responses = staircase.data

intensities = np.array([.7,.7,.7,.7,.7,.8,.8,.8,.8,.9,.9,.9,1.0,1.0,1.0,1.5,2.0,2.0,2.0]) #debug, example data
responses= np.array([0,0,0,0,0 ,     0,1,0,0,     1,1,0,    1,1,1,   1,     1,1,1]) #debug, example data
#
expectedMin = 1.0/26
#fit curve
threshVal = 0.9 #threshVal is proportion correct for which want to estimate the parameter (intensity) level
fit = data.FitWeibull(intensities, responses, expectedMin=expectedMin,   sems = 1.0/len(intensities))
plotDataAndPsychometricCurve(intensities,responses,fit,threshVal)
#save figure to file
dataDir = 'data'
outputFile = os.path.join(dataDir, 'test.pdf')
pylab.savefig(outputFile)
pylab.show() #must call this to actually show plot
