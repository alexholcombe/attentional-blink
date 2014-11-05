#Jan 2012 start. Implementation of attentional blink task. Also see Martini 2012 Attention Perception & Psychophysics "SOURCES OF BIAS AND UNCERTAINTY IN A VISUAL TEMPORAL INDIVIDUATION TASK"
#Alex Holcombe alex.holcombe@sydney.edu.au
#licensing: CC-BY whch means do whatever you want with it, with an attribution to the author. If you want permission to use it without attribution, contact me.
#5 Nov. Starting with non-git AB_addNoise_QUEST2.py

from __future__ import print_function
from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan, log, ceil
from copy import deepcopy
import itertools, time, sys, os
#Empirical background:
#Martini AB data were the averages of 20 undergrads. Each contributed 4 consecutive blocks of 100 trials, total time about 35 minutes. The parameters were identical to Vul 2008, 
#with a duticycle of 90ms (~11 Hz) and each character shown for 3 frames (33 ms at 90 Hz framerate). Note that in those conditions the bottom of AB at lags 2 and 3 is effectively at chance, so there may be a floor effect there.

#In experiment 1b I used 15Hz streams, 2 blocks of 100 trials, and that takes roughly 12-15 minutes.
#There is some learning, Paolo measured it in experiment 1a with repeat subjects (graph attached), so you should check whether your effects would be washed out by this. 
#Also, experiment 1b was run with T1 fixed, i.e. the cue was always in the midstream position.

tasks=['T1','T1T2']; task = tasks[1]
refreshRate=60 #90 Hz used by Paolo  #set to the framerate of the monitor
#THINGS THAT COULD PREVENT SUCCESS ON A STRANGE MACHINE
#same screen or external screen? scrn
#Hz wrong, widthPix, heightPix
demo=False #False
exportImages= False#quits after one trial
autopilot=False
subject='Hubert' #user is prompted to enter replacement name
if autopilot: subject='auto'
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print('"data" directory does not exist, so saving data in present working directory')
    dataDir='.'
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, so visualize missed frames
feedback=False #Martini didn't include feedback
autoLogging=False
if demo:
    refreshRate = 60.;  #100

staircaseTrials = 10
nEasyStaircaseStarterTrials = 3;
easyStaircaseStarterNoise = np.array([2, 2, 5, 5, 10, 80, 80, 80])#,30, 80, 40, 90, 30, 70, 30, 40, 80, 20, 20, 50 ]

bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [1.,1.,1.]
letterColor = [1.,1.,1.]
cueRadius = 6 #6 deg, as in Martini E2    Letters should have height of 2.5 deg
#letter size 2.5 deg
numLettersToPresent = 26
SOAms = 133
#Minimum SOAms should be 84  because any shorter, I can't always notice the second ring when lag1.   71 in Martini E2 and E1b (actually he used 66.6 but that's because he had a crazy refresh rate of 90 Hz)
letterDurMs = 80 #23.6  in Martini E2 and E1b (actually he used 22.2 but that's because he had a crazy refresh rate of 90 Hz)

ISIms = SOAms - letterDurMs
letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
cueDurFrames = letterDurFrames
ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
#have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
rateInfo = 'total SOA=' + str(round(  (ISIframes + letterDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + letterDurFrames) + ' frames, comprising\n'
rateInfo+=  'ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and letterDurFrames ='+str(letterDurFrames)+' or '+str(round( letterDurFrames*(1000./refreshRate), 2))+'ms'
print(rateInfo)

trialDurFrames = int( numLettersToPresent*(ISIframes+letterDurFrames) ) #trial duration in frames

widthPix= 1024 #1280 #monitor width in pixels
heightPix= 768  #800 #800 #monitor height in pixels
monitorwidth = 38.7 #monitor width in cm
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
fullscr=0 #1
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 400; heightPix = 400
    monitorwidth = 13.0
    fullscr=0; scrn=0
if demo:    
    scrn=0; fullscr=0
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
viewdist = 57. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
print('pixelperdegree=',pixelperdegree)

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
#Have to close window, then open it again
quitFinder = True
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
 
 # Then gather run-time info. All parameters are optional:
runInfo = psychopy.info.RunTimeInfo(
        # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
        #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
        #version="<your experiment version info>",
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
#print(runInfo)
logging.info(runInfo)

#check screen refresh is what assuming it is ########################################################################
Hzs=list()
myWin.flip(); myWin.flip();myWin.flip();myWin.flip();
myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
for i in range(50):
    myWin.flip()
    Hzs.append( myWin.fps() )  #varies wildly on successive runs!
myWin.setRecordFrameIntervals(False)
# end testing of screen refresh########################################################################
Hzs = np.array( Hzs );     Hz= np.median(Hzs)
msPerFrame= 1000./Hz
refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
refreshRateTolerancePct = 3
pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
refreshMsg2 = ''
if refreshRateWrong:
    refreshMsg1 += ' BUT'
    refreshMsg1 += ' program assumes ' + str(refreshRate)
    refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
else:
    refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
refreshMsg3= ''
myWinRes = myWin.size
myWin.close() #have to close window to show dialog box
myWin.allowGUI =True
trialsPerCondition = 8 #default value
dlgLabelsOrdered = list()
myDlg = gui.Dlg(title="RSVP experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name (default="Hubert"):', tip='or subject code')
    dlgLabelsOrdered.append('subject')
dlgLabelsOrdered.append('staircaseTrials')
myDlg.addField('Staircase trials (default=' + str(staircaseTrials) + '):',    tip=str(staircaseTrials))
easyTrialsCondText = 'Num low-noise trials to begin staircase with (default=' + str(nEasyStaircaseStarterTrials) + '):'
myDlg.addField(easyTrialsCondText, tip=str(nEasyStaircaseStarterTrials))
dlgLabelsOrdered.append('easyTrials')
myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', tip=str(trialsPerCondition))
dlgLabelsOrdered.append('trialsPerCondition')

myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
myDlg.addText(refreshMsg3, color='Black')
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)
#myDlg.addText(phasesMsg, color='Black')

if (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.error(msgWrongResolution)
    print(msgWrongResolution)
myDlg.addText('Note: during the experiment, press ESC at response screen to quit', color=[-1.,1.,-1.]) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()

if myDlg.OK:
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
   if len(thisInfo[dlgLabelsOrdered.index('trialsPerCondition')]) > 0: #if entered something for trialsPerCondition
       trialsPerCondition = int( thisInfo[trialsField] ) #convert string to integer
       print('trialsPerCondition entered by user=',trialsPerCondition)
       logging.info('trialsPerCondition entered by user=',trialsPerCondition)
   if len(thisInfo[dlgLabelsOrdered.index('staircaseTrials')]) >0:
       staircaseTrials = int( thisInfo[ dlgLabelsOrdered.index('staircaseTrials') ] ) #convert string to integer
       print('staircaseTrials entered by user=',staircaseTrials)
       logging.info('staircaseTrials entered by user=',staircaseTrials)
   if len(thisInfo[dlgLabelsOrdered.index('easyTrials')]) >0:
       nEasyStaircaseStarterTrials = int( thisInfo[ dlgLabelsOrdered.index('easyTrials') ] ) #convert string to integer
       print('nEasyStaircaseStarterTrials entered by user=',thisInfo[dlgLabelsOrdered.index('easyTrials')])
       logging.info('nEasyStaircaseStarterTrials entered by user=',nEasyStaircaseStarterTrials)
else: 
   print('user cancelled')
   logging.flush()
   core.quit()
if not demo: 
    myWin.allowGUI = False

myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor

#set up output data file, log file,  copy of program code, and logging
fileName = dataDir+'/'+subject+'_'+timeAndDateStr
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')  # sys.stdout  
    saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
    os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
    logFname = fileName+'.log'
    ppLogF = logging.LogFile(logFname, 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout; logF = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.ERROR) #DEBUG means set  console to receive nearly all messges, INFO next level, EXP, DATA, WARNING and ERROR 

logging.info(rateInfo)

if fullscr and not demo and not exportImages:
    runInfo = psychopy.info.RunTimeInfo(
        # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
        #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
        #version="<your experiment version info>",
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=False, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        #randomSeed='set:42', ## a way to record, and optionally set, a random seed of type str for making reproducible random sequences
            ## None -> default 
            ## 'time' will use experimentRuntime.epoch as the value for the seed, different value each time the script is run
            ##'set:time' --> seed value is set to experimentRuntime.epoch, and initialized: random.seed(info['randomSeed'])
            ##'set:42' --> set & initialize to str('42'), and will give the same sequence of random.random() for all runs of the script
        )
    logging.info(runInfo)
logging.flush()

#create click sound for keyboard
try:
    click=sound.Sound('406__tictacshutup__click-1-d.wav')
except: #in case file missing, create inferiro click manually
    logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
    click=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)

if showRefreshMisses:
    fixSizePix = 32 #2.6  #make fixation bigger so flicker more conspicuous
else: fixSizePix = 32
fixColor = [1,1,1]
if exportImages: fixColor= [0,0,0]
fixatnNoiseTexture = np.round( np.random.rand(fixSizePix/4,fixSizePix/4) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation

fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False)
fixationBlank= visual.PatchStim(myWin, tex= -1*fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False) #reverse contrast
fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(1,1,1),size=10,units='pix',autoLog=autoLogging)
respPromptText = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
respText = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)
screenshot= False; screenshotDone = False
stimList = []

possibleCue1positions = np.array([6,7,8,9,10]) # [4,10,16,22] used in Martini E2, group 2
possibleCue2lags = np.array([1,2,5,8,10])   #[1,2,5,10]
for cue1pos in possibleCue1positions:
   for cue2lag in possibleCue2lags:
        stimList.append( {'cue1pos':cue1pos, 'cue2lag':cue2lag } )
#Martini E2 and also AB experiments used 400 trials total, with breaks between every 100 trials

trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method
trialsForPossibleStaircase = data.TrialHandler(stimList,trialsPerCondition) #independent randomization, just to create random trials for staircase phase
numRightWrongEachCuepos = np.zeros([ len(possibleCue1positions), 1 ]); #summary results to print out at end
numRightWrongEachCue2lag = np.zeros([ len(possibleCue2lags), 1 ]); #summary results to print out at end

logging.info( 'numtrials=' + str(trials.nTotal) + ' and each trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' + '  task=' + task)
print(' numtrials=', trials.nTotal)

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

def letterToNumber(letter): #A = 0, Z = 25
    #if it's not really a letter, return -999
    #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT' SNOT PART OF AN ARRAY?
    try:
        #if len(letter) > 1:
        #    return (-999)
        if letter < 'A' or letter > 'Z':
            return (-999)
        else: #it's a letter
            return ord(letter)-ord('A')
    except:
        return (-999)

def printStaircaseStuff(staircase, briefTrialUpdate, alsoLog=False):
    #if briefTrialUpdate, don't print everything, just the kind of stuff you like to know after each trial
    #needs logging as a global variable, otherwise will fail when alsoLog=True
    msg = 'staircase.data (incorrect/correct)=' + str(staircase.data)
    print(msg)
    if alsoLog:     logging.info(msg)
    
    if staircase.stepType == 'log':
        msg = 'staircase.intensities (these are log intensities)=['
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
        msg= 'number of reversals=' + str(numReversals) + ']n'
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
                msg= ('pThreshold (proportion correct for which trying to zero in on the corresponding parameter value) =' +
                               str(staircase._quest.pThreshold) + '\n')
                msg+= ('stopInterval (min 5-95% confidence interval required for  thresh  before stopping. If both this and nTrials is specified, whichever happens first)='+
                               str(staircase.stopInterval) + '\n')
                msg+= 'stepType=' + str(staircase.stepType) + '\n'
                msg+= 'minVal=' + str(staircase.minVal) + '  maxVal=' + str(staircase.maxVal) + '\n'
                msg+= 'nTrials=' + str(staircase.nTrials)
                print(msg)
                if alsoLog:     logging.info(msg)

    #below applies to both types of staircase
    if staircase.thisTrialN == -1:
        msg= 'thisTrialN = -1, suggesting you have not started it yet; need to call staircase.next()'
        print(msg)
        if alsoLog:     logging.info(msg)
    else:
        msg= 'thisTrialN (current trial number) =' + str(staircase.thisTrialN)
        print(msg)
        if alsoLog:     logging.info(msg)
        # staircase.calculateNextIntensity() sounds like something useful to get a preview of the next trial. Instead, seems to be 
        #the internal function used to advance to the next trial.
    
def createNoiseArray(proportnNoise,fieldWidthPix): 
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
    noise = visual.ElementArrayStim(myWin,units='pix', elementTex=None, elementMask=None,
        nElements=numDots, fieldSize=[fieldWidthPix,fieldWidthPix],
        fieldPos=(0.0, verticalAdjust),
        colorSpace='rgb',
        colors=-1, #set to black
        xys= dotCoords, 
        opacities=opacs,
        sizes=1)
    return (noise,allFieldCoords,numDots) #Can just use noise, but if want to generate new noise of same coherence level quickly, can just shuffle coords


#print header for data file
print('trialnum\tsubject\ttask\t',file=dataFile,end='')
if task=='T1':
    numRespsWanted = 1
elif task=='T1T2':
    numRespsWanted = 2
for i in range(numRespsWanted):
   dataFile.write('answerPos'+str(i)+'\t')   #have to use write to avoid ' ' between successive text, at least until Python 3
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
   dataFile.write('responsePosRelative'+str(i)+'\t')
print('timingBlips',file=dataFile)
#end of header

def  oneFrameOfStim( n,cue,letterSequence,cueDurFrames,letterDurFrames,ISIframes,cuesPos,lettersDrawObjects,
                                       noise,proportnNoise,allFieldCoords,numNoiseDots ): 
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
  SOAframes = letterDurFrames+ISIframes
  cueFrames = cuesPos*SOAframes  #cuesPos is global variable
  letterN = int( np.floor(n/SOAframes) )
  frameOfThisLetter = n % SOAframes #every SOAframes, new letter
  showLetter = frameOfThisLetter < letterDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
  #print 'n=',n,' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes)  #DEBUGOFF
  thisLetterIdx = letterSequence[letterN] #which letter, from A to Z (1 to 26), should be shown?
  #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
  cue.setLineColor( bgColor )
  for cueFrame in cueFrames: #cheTck whether it's time for any cue
      if n>=cueFrame and n<cueFrame+cueDurFrames:
         cue.setLineColor( cueColor )

  if showLetter:
     lettersDrawObjects[thisLetterIdx].setColor( letterColor )
  else: lettersDrawObjects[thisLetterIdx].setColor( bgColor )
  
  lettersDrawObjects[thisLetterIdx].draw()
  cue.draw()
  refreshNoise = False #Not recommended because takes longer than a frame, even to shuffle apparently. Or may be setXYs step
  if proportnNoise>0 and refreshNoise: 
    if frameOfThisLetter ==0: 
        np.random.shuffle(allFieldCoords) 
        dotCoords = allFieldCoords[0:numNoiseDots]
        noise.setXYs(dotCoords)
  if proportnNoise>0:
    noise.draw()
  return True 
# #######End of function definition that displays the stimuli!!!! #####################################

def collectResponses(task,numRespsWanted,responseDebug=False): 
    event.clearEvents() #clear the keyboard buffer
    expStop = False
    passThisTrial = False
    respStr = ''
    responses=[]
    numResponses = 0
    while numResponses < numRespsWanted and not expStop:
        #print 'numResponses=', numResponses #debugOFF
        noResponseYet=True
        thisResponse=''
        while noResponseYet: #collect one response
           respPromptText.draw()
           #respStr= 'Y'
           #print 'respStr = ', respStr, ' type=',type(respStr) #debugOFF
           respText.setText(respStr,log=False)
           respText.draw()
           myWin.flip()
           for key in event.getKeys():       #check if pressed abort-type key
                  key = key.upper()
                  thisResponse = key
                  if key in ['ESCAPE']:
                      expStop = True
                      noResponseYet = False
#                  if key in ['SPACE']: #observer opting out because think they moved their eyes
#                      passThisTrial = True
#                      noResponseYet = False
                  if key in ['A', 'C', 'B', 'E', 'D', 'G', 'F', 'I', 'H', 'K', 'J', 'M', 'L', 'O', 'N', 'Q', 'P', 'S', 'R', 'U', 'T', 'W', 'V', 'Y', 'X', 'Z']:
                      noResponseYet = False
           if autopilot:
               noResponseYet=False
        #click to provide feedback that response collected. Eventually, draw on screen
        click.play()
        if thisResponse or autopilot:
            responses.append(thisResponse)
            numResponses += 1 #not just using len(responses) because want to work even when autopilot, where thisResponse is null
        respStr = ''.join(responses) #converts list of characters (responses) into string
        #print 'responses=',responses,' respStr = ', respStr #debugOFF
        respText.setText(respStr,log=False); respText.draw(); myWin.flip() #draw again, otherwise won't draw the last key
        
    responsesAutopilot = np.array(   numRespsWanted*list([('A')])        )
    responses=np.array( responses )
    #print 'responses=', responses,' responsesAutopilot=', responsesAutopilot #debugOFF
    return expStop,passThisTrial,responses,responsesAutopilot
# #######End of function definition that collects responses!!!! #####################################
#############################################################################################################################

cue = visual.Circle(myWin, 
                 radius=cueRadius,#Martini used circles with diameter of 12 deg
                 lineColorSpace = 'rgb',
                 lineColor=bgColor,
                 lineWidth=2.0, #in pixels
                 units = 'deg',
                 fillColorSpace = 'rgb',
                 fillColor=None, #beware, with convex shapes fill colors don't work
                 pos= [0,0], #the anchor (rotaion and vertices are position with respect to this)
                 interpolate=True,
                 autoLog=False)#this stim changes too much for autologging to be useful

#predraw all 26 letters 
ltrHeight = 2.5 #Martini letters were 2.5deg high
lettersDrawObjects = list()
for i in range(0,26):
   letterDraw = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
   letterDraw.setHeight( ltrHeight )
   letter = numberToLetter(i)
   letterDraw.setText(letter,log=False)
   letterDraw.setColor(bgColor)
   lettersDrawObjects.append(letterDraw)

#All noise dot coordinates ultimately in pixels, so can specify each dot is one pixel 
noiseFieldWidthDeg=ltrHeight *1.0
noiseFieldWidthPix = int( round( noiseFieldWidthDeg*pixelperdegree ) )

def timingCheckAndLog(ts):
    #check for timing problems and log them
    #ts is a list of the times of the clock after each frame
    interframeIntervs = np.diff(ts)*1000
    #print '   interframe intervs were ',around(interframeIntervs,1) #DEBUGOFF
    frameTimeTolerance=.3 #proportion longer than refreshRate that will not count as a miss
    longFrameLimit = np.round(1000/refreshRate*(1.0+frameTimeTolerance),2)
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded 150% of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0 and (not demo):
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                logging.error( 'trialnum='+str(trialN)+' '+longFramesStr )
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:
                            flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    flankingAlso = np.array(flankingAlso)
                    flankingAlso = flankingAlso[np.negative(np.isnan(flankingAlso))]  #remove nan values
                    flankingAlso = flankingAlso.astype(np.integer) #cast as integers, so can use as subscripts
                    logging.info( 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )  ) #because this is not an essential error message, as previous one already indicates error
                      #As INFO, at least it won't fill up the console when console set to WARNING or higher
    return numCasesInterframeLong
    #end timing check
    
trialClock = core.Clock()
numTrialsCorrect = 0; 
numTrialsApproxCorrect = 0;
numTrialsEachCorrect= np.zeros( numRespsWanted )
numTrialsEachApproxCorrect= np.zeros( numRespsWanted )

def do_RSVP_stim(cue1pos, cue2lag, proportnNoise,trialN):
    #relies on global variables:
    #   logging, 
    #
    cuesPos = [] #will contain the positions of all the cues (targets)
    cuesPos.append(cue1pos)
    if task=='T1T2':
        cuesPos.append(cue1pos+cue2lag)
    cuesPos = np.array(cuesPos)
    letterSequence = np.arange(0,26)
    np.random.shuffle(letterSequence)
    correctAnswers = np.array( letterSequence[cuesPos] )
    print ('first several lines done of do_RSVP_stim') #debugON
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #generating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
        (noise,allFieldCoords,numNoiseDots) = createNoiseArray(proportnNoise,noiseFieldWidthPix) 

    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I have consistent timing blip first time that draw ringInnerR for phantom contours
    cue.setLineColor(bgColor)
    preDrawStimToGreasePipeline.extend([cue])
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    myWin.flip(); myWin.flip()
    #end preparation of stimuli
    
    core.wait(.1);
    trialClock.reset()
    fixatnPeriodMin = 0.3
    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+fixatnPeriodMin)   *refreshRate)  #random interval between 800ms and 1.3s (changed when Fahed ran outer ring ident)
    ts = list(); #to store time of each drawing, to check whether skipped frames
    for i in range(fixatnPeriodFrames+20):  #prestim fixation interval
        #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
        #      fixation.draw()
        #else: fixationBlank.draw()
        fixationPoint.draw()
        myWin.flip()  #end fixation interval
    #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
    t0 = trialClock.getTime()

    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
        worked = oneFrameOfStim( n,cue,letterSequence,cueDurFrames,letterDurFrames,ISIframes,cuesPos,lettersDrawObjects,
                                                     noise,proportnNoise,allFieldCoords,numNoiseDots) #draw letter and possibly cue and noise on top
        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1              
        myWin.flip()
        t=trialClock.getTime()-t0;  ts.append(t);
    #end of big stimulus loop
    myWin.setRecordFrameIntervals(False);

    if task=='T1':
        respPromptText.setText('Which letter was circled?',log=False)
    elif task=='T1T2':
        respPromptText.setText('Which two letters were circled?',log=False)
    else: respPromptText.setText('Error: unexpected task',log=False)
    postCueNumBlobsAway=-999 #doesn't apply to non-tracking and click tracking task
    print('About to return from do_RSVP_stim') #debugON
    return letterSequence,cuesPos,correctAnswers, ts  
    
def handleAndScoreResponse(expStop,passThisTrial,responses,responsesAutopilot,task,letterSequence,cuesPos,correctAnswers):
    #Handle response, calculate whether correct, ########################################
    if expStop:
        responses =np.array([-999])  #because otherwise responses can't be turned into array if have partial response
        correct=0
    if autopilot or passThisTrial:
        responses = responsesAutopilot;  #print('assigning responses to responsesAutopilot, = ', responsesAutopilot)
    
    eachCorrect = np.zeros( len(correctAnswers) )
    eachApproxCorrect = np.zeros( len(correctAnswers) )
    posOfResponse = np.zeros( len(cuesPos) )
    responsePosRelative = np.zeros( len(cuesPos) )
    print('About to score responses') #debugON

    if expStop:
        pass
    else:
        for i in range(len(cuesPos)): #score response to each cue
            if correctAnswers[i] == letterToNumber( responses[i] ):
                eachCorrect[i] = 1
            posThisResponse= np.where( letterToNumber(responses[i])==letterSequence )
            #print 'responses=',responses,'posThisResponse raw=',posThisResponse, ' letterSequence=',letterSequence #debugOFF
            posThisResponse= posThisResponse[0] #list with potentially two entries, want first which will be array of places where the reponse was found in the letter sequence
            if len(posThisResponse) > 1:
                logging.error('Expected response to have occurred in only one position in stream')        
            if np.alen(posThisResponse)==0: #response not found in letter sequence
                posThisResponse = -999
                logging.warn('Response was not present in the stimulus stream')
            else: 
                posThisResponse = posThisResponse[0]
            posOfResponse[i]= posThisResponse
            responsePosRelative[i] = posOfResponse[i] - cuesPos[i]
            eachApproxCorrect[i] +=   abs(responsePosRelative[i]) <= 3 #Vul efficacy measure of getting it right to within plus/minus 
        #header start      'trialnum\tsubject\ttask\t'
        print(subject,'\t',task,'\t', end='', file=dataFile)
        for i in range(len(cuesPos)):
            #header continued.  answerPos0, answer0, response0, correct0, responsePosRelative0
            print(cuesPos[i],'\t', end='', file=dataFile)
            answerCharacter = numberToLetter( letterSequence [cuesPos[i] ] )
            print(answerCharacter, '\t', end='', file=dataFile) #answer0
            print(responses[i], '\t', end='', file=dataFile) #response0
            print(eachCorrect[i] , '\t', end='',file=dataFile)   #correct0
            print(responsePosRelative[i], '\t', end='',file=dataFile) #responsePosRelative0

        print('Have scored responses.') #debugON

        correct = eachCorrect.all() 
        T1approxCorrect = eachApproxCorrect[0]

        print('Got to last line of do_RSVP_trial') #debugON
        return correct,eachApproxCorrect,T1approxCorrect,passThisTrial,expStop
        #end handleAndScoreResponses

def play_high_tone_correct_low_incorrect(correct, passThisTrial=False):
    highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3, bits=8)
    low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3, bits=8)
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
        for i in range(2): 
            high.play();  low.play(); 
    else: #incorrect
        low.play()

#create the staircase handler
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
                          stopInterval= 1, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                          nTrials = staircaseTrials,
                          #extraInfo = thisInfo,
                          pThreshold = 0.90, #0.25,    
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

doingStaircasePhase = False #First phase of experiment is method of constant stimuli. If use naked QUEST, might converge too soon
easyStaircaseStarterNoise = np.array([2, 5, 10, 80])#,30, 80, 40, 90, 30, 70, 30, 40, 80, 20, 20, 50 ]
if nEasyStaircaseStarterTrials > len(easyStaircaseStarterNoise): #repeat array to accommodate desired number of easyStarterTrials
    easyStaircaseStarterNoise = np.tile( easyStaircaseStarterNoise, ceil( nEasyStaircaseStarterTrials/len(easyStaircaseStarterNoise) ) )
easyStaircaseStarterNoise = easyStaircaseStarterNoise[0:nEasyStaircaseStarterTrials]

phasesMsg = ('Starting with '+str(nEasyStaircaseStarterTrials)+' of noise= '+str(easyStaircaseStarterNoise)+' then doing a max '+str(staircaseTrials)+'-trial staircase' +
                        ' followed by '+str(trials.nTotal)+' trials at that noise level') #parentheses purely for line continuation
print(phasesMsg)

expStop=False; framesSaved=0

corrEachTrial = list() #only needed for easyStaircaseStarterNoise
staircaseTrialN = -1; mainStaircaseGoing = False
while (not staircase.finished) and expStop==False: #staircase.thisTrialN < staircase.nTrials
    if staircaseTrialN+1 < len(easyStaircaseStarterNoise): #still doing easyStaircaseStarterNoise
        staircaseTrialN += 1
        percentNoise = easyStaircaseStarterNoise[staircaseTrialN]
    else:
        if staircaseTrialN+1 == len(easyStaircaseStarterNoise): #add these non-staircase trials so QUEST knows about them
            mainStaircaseGoing = True
            print('Readying to import ',corrEachTrial,' and intensities ',easyStaircaseStarterNoise)
            staircase.importData(100-easyStaircaseStarterNoise, np.array(corrEachTrial)) 
        try: #advance the staircase
            printStaircaseStuff(staircase, briefTrialUpdate=True, alsoLog=False)
            percentNoise = 100- staircase.next()  #will step through the staircase, based on whether told it (addData) got it right or wrong
            print('Staircase advanced, percentNoise for this trial = ', np.around(percentNoise,2)) #debugON
            staircaseTrialN += 1
        except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
            print('stopping because staircase.next() returned a StopIteration, which it is supposed to do when it is finished')
            break #break out of the trials loop
    print('staircaseTrialN=',staircaseTrialN)
    
    letterSequence,cuesPos,correctAnswers, ts  = do_RSVP_stim(cue1pos, cue2lag, percentNoise/100.,staircaseTrialN)
    numCasesInterframeLong = timingCheckAndLog(ts)
    
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop,passThisTrial,responses,responsesAutopilot = \
                collectResponses(task,numRespsWanted,responseDebug=True)
    print(staircaseTrialN,'\t', file=dataFile) #first thing printed on each line of dataFile
    correct,eachApproxCorrect,T1approxCorrect,passThisTrial,expStop = (
            handleAndScoreResponse(expStop,passThisTrial,responses,responsesAutopilot,task,letterSequence,cuesPos,correctAnswers) )
    print('staircase\t', numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
    core.wait(.06)
    if feedback: 
        play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
    print('expStop=',expStop,'   T1approxCorrect=',T1approxCorrect) #debugON
    corrEachTrial.append(T1approxCorrect)
    if mainStaircaseGoing: 
        staircase.addResponse(T1approxCorrect, intensity = 100-percentNoise) #Add a 1 or 0 to signify a correct/detected or incorrect/missed trial

timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
mainStaircaseGoing = False
msg='Finished staircase component of experiment at ' + timeAndDateStr
logging.info(msg); print(msg)
printStaircaseStuff(staircase, briefTrialUpdate=False, alsoLog=True)
msg='Staircase estimate of threshold = ' + 100- np.around(staircase.quantile,3) + ' with sd =', staircase.sd()
logging.info(msg); print(msg)

expStop = False
msg='Starting main (non-staircase) part of experiment'
logging.info(msg); print(msg)
nDoneAfterStaircase =0
while nDoneAfterStaircase < trials.nTotal and expStop==False:
    thisTrial = trials.next() #get a proper (non-staircase) trial
    cue1pos = thisTrial['cue1pos']
    cue2lag = thisTrial['cue2lag']
    letterSequence,cuesPos,correctAnswers, ts  = do_RSVP_stim(cue1pos, cue2lag, percentNoise/100.,staircaseTrialN)
    numCasesInterframeLong = timingCheckAndLog(ts)
    
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop,passThisTrial,responses,responsesAutopilot = \
                collectResponses(task,numRespsWanted,responseDebug=True)
    print(staircaseTrialN,'\t', file=dataFile) #first thing printed on each line of dataFile
    correct,eachApproxCorrect,T1approxCorrect,passThisTrial,expStop = (
            handleAndScoreResponse(expStop,passThisTrial,responses,responsesAutopilot,task,letterSequence,cuesPos,correctAnswers) )
    print('afterStaircase\t', numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile

    numTrialsCorrect += correct #so count -1 as 0
    numTrialsApproxCorrect += eachApproxCorrect.all()
    numTrialsEachCorrect += eachCorrect
    numTrialsEachApproxCorrect += eachApproxCorrect
        
    if exportImages:  #catches one frame of response
         myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
         framesSaved +=1; core.wait(.1)
         myWin.saveMovieFrames('exported/frames.mov')  
         expStop=True
    core.wait(.1)
    if feedback: play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
    if not expStop:
        nDoneAfterStaircase+=1
    
    dataFile.flush(); logging.flush()
    #print 'nDone=', nDone,' trials.thisN=',trials.thisN,' trials.nTotal=',trials.nTotal
    core.wait(.2); time.sleep(.2)
    #end trials loop
timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
msg = 'finishing at '+timeAndDateStr
print(msg);  logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials done='+ str(nDoneAfterStaircase) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.error(msg)

print('Of ',nDoneAfterStaircase,' trials, ',numTrialsCorrect*1.0/nDoneAfterStaircase*100., '% exactly correct',sep='')
print('All targets approximately correct in ',round(numTrialsApproxCorrect*1.0/nDoneAfterStaircase*100,1),'% of trials',sep='')
print('T1: ',round(numTrialsEachCorrect[0]*1.0/nDoneAfterStaircase*100.,2), '% correct',sep='')
if len(numTrialsEachCorrect) >1:
    print('T2: ',round(numTrialsEachCorrect[1]*1.0/nDoneAfterStaircase*100,2),'% correct',sep='')
print('T1: ',round(numTrialsEachApproxCorrect[0]*1.0/nDoneAfterStaircase*100,2),'% approximately correct',sep='')
if len(numTrialsEachCorrect) >1:
    print('T2:',round(numTrialsEachApproxCorrect[1]*1.0/nDoneAfterStaircase*100,2),'% approximately correct',sep='')

   #print 'breakdown by speed: ',
   #print numRightWrongEachSpeedOrder[:,1] / ( numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1])   
#contents = dataFile.getvalue(); print contents
#contents = logF.getvalue(); print contents
logging.flush(); dataFile.close()