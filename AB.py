#Alex Holcombe alex.holcombe@sydney.edu.au
#See the README.md for more information: https://github.com/alexholcombe/attentional-blink/blob/master/README.md
#git remote add origin https://github.com/alexholcombe/attentional-blink.git
from __future__ import print_function
from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan, log, ceil
from copy import deepcopy
import time, sys, os, pylab
from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
descendingPsycho = True
tasks=['T1','T1T2']; task = tasks[1]
#THINGS THAT COULD PREVENT SUCCESS ON A STRANGE MACHINE
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix
quitFinder = False #if checkRefreshEtc, quitFinder becomes True
autopilot=False
demo=False #False
exportImages= False #quits after one trial
subject='Hubert' #user is prompted to enter true subject name
if autopilot: subject='auto'
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print('"data" directory does not exist, so saving data in present working directory')
    dataDir='.'
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=False #Martini didn't include feedback
autoLogging=False
if demo:
    refreshRate = 60.;  #100

staircaseTrials = 25
prefaceStaircaseTrialsN = 20 #22
prefaceStaircaseNoise = np.array([5,20,20,20, 50,50,50,5,80,80,80,5,95,95,95]) #will be recycled / not all used, as needed
threshCriterion = 0.58
bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [1.,1.,1.]
letterColor = [1.,1.,1.]
cueRadius = 6 #6 deg, as in Martini E2    Letters should have height of 2.5 deg

widthPix= 1280 #monitor width in pixels of Agosta
heightPix= 800 #800 #monitor height in pixels
monitorwidth = 38.7 #monitor width in cm
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
fullscr=True #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 400; heightPix = 400
    monitorwidth = 13.0
    fullscr=False; scrn=0
if demo:    
    scrn=0; fullscr=False
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
viewdist = 57. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
print('pixelperdegree=',pixelperdegree)
    
# create a dialog from dictionary 
infoFirst = { 'Do staircase (only)': False, 'Check refresh etc':True, 'Fullscreen (timing errors if not)': True, 'Screen refresh rate': 60 }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='AB experiment OR staircase to find thresh noise level for T1 performance criterion', 
    order=['Do staircase (only)', 'Check refresh etc', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating'},
    #fixed=['Check refresh etc'])#this attribute can't be changed by the user
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
doStaircase = infoFirst['Do staircase (only)']
checkRefreshEtc = infoFirst['Check refresh etc']
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']
if checkRefreshEtc:
    quitFinder = True 
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)

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
logging.info(rateInfo); print(rateInfo)

trialDurFrames = int( numLettersToPresent*(ISIframes+letterDurFrames) ) #trial duration in frames

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()
refreshMsg2 = ''
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    #print(runInfo)
    logging.info(runInfo)
    print('Finished runInfo- which assesses the refresh and processes of this computer') 
    #check screen refresh is what assuming it is ##############################################
    Hzs=list()
    myWin.flip(); myWin.flip();myWin.flip();myWin.flip();
    myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
    print('About to measure frame flips') 
    for i in range(50):
        myWin.flip()
        Hzs.append( myWin.fps() )  #varies wildly on successive runs!
    myWin.setRecordFrameIntervals(False)
    # end testing of screen refresh########################################################
    Hzs = np.array( Hzs );     Hz= np.median(Hzs)
    msPerFrame= 1000./Hz
    refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True
myWin.close() #have to close window to show dialog box

defaultNoiseLevel = 0.0 #to use if no staircase, can be set by user
trialsPerCondition = 8 #default value
dlgLabelsOrdered = list()
if doStaircase:
    myDlg = gui.Dlg(title="Staircase to find appropriate noisePercent", pos=(200,400))
else: 
    myDlg = gui.Dlg(title="RSVP experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name (default="Hubert"):', tip='or subject code')
    dlgLabelsOrdered.append('subject')
if doStaircase:
    easyTrialsCondText = 'Num preassigned noise trials to preface staircase with (default=' + str(prefaceStaircaseTrialsN) + '):'
    myDlg.addField(easyTrialsCondText, tip=str(prefaceStaircaseTrialsN))
    dlgLabelsOrdered.append('easyTrials')
    myDlg.addField('Staircase trials (default=' + str(staircaseTrials) + '):', tip="Staircase will run until this number is reached or it thinks it has precise estimate of threshold")
    dlgLabelsOrdered.append('staircaseTrials')
    pctCompletedBreak = 101
else:
    myDlg.addField('\tPercent noise dots=',  defaultNoiseLevel, tip=str(defaultNoiseLevel))
    dlgLabelsOrdered.append('defaultNoiseLevel')
    myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', tip=str(trialsPerCondition))
    dlgLabelsOrdered.append('trialsPerCondition')
    pctCompletedBreak = 50
    
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)

if checkRefreshEtc and (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.error(msgWrongResolution)
    print(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen', color=[-1.,1.,-1.]) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()

if myDlg.OK: #unpack information from dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
   if doStaircase:
       if len(thisInfo[dlgLabelsOrdered.index('staircaseTrials')]) >0:
           staircaseTrials = int( thisInfo[ dlgLabelsOrdered.index('staircaseTrials') ] ) #convert string to integer
           print('staircaseTrials entered by user=',staircaseTrials)
           logging.info('staircaseTrials entered by user=',staircaseTrials)
       if len(thisInfo[dlgLabelsOrdered.index('easyTrials')]) >0:
           prefaceStaircaseTrialsN = int( thisInfo[ dlgLabelsOrdered.index('easyTrials') ] ) #convert string to integer
           print('prefaceStaircaseTrialsN entered by user=',thisInfo[dlgLabelsOrdered.index('easyTrials')])
           logging.info('prefaceStaircaseTrialsN entered by user=',prefaceStaircaseTrialsN)
   else: #not doing staircase
       if len(thisInfo[dlgLabelsOrdered.index('trialsPerCondition')]) > 0: #if entered something for trialsPerCondition
           trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
           print('trialsPerCondition entered by user=',trialsPerCondition)
           logging.info('trialsPerCondition entered by user=',trialsPerCondition)
       defaultNoiseLevel = int (thisInfo[ dlgLabelsOrdered.index('defaultNoiseLevel') ])
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()
if not demo: 
    allowGUI = False

myWin = openMyStimWindow()
#set up output data file, log file,  copy of program code, and logging
infix = ''
if doStaircase:
    infix = 'staircase_'
fileName = os.path.join(dataDir, subject + '_' + infix+ timeAndDateStr)
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')
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
nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
screenshot= False; screenshotDone = False
stimList = []

#SETTING THE CONDITIONS
possibleCue1positions =  np.array([6,7,8,9,10]) # [4,10,16,22] used in Martini E2, group 2
possibleCue2lags = np.array([1,2,5,8,10]) 
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

#print header for data file
print('experimentPhase\ttrialnum\tsubject\ttask\t',file=dataFile,end='')
print('noisePercent\t',end='',file=dataFile)
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
               noResponseYet = False
               for key in event.getKeys():    #check if pressed abort-type key. But in autopilot so not in a loop, so have to get lucky
                      key = key.upper()
                      thisResponse = key
                      if key in ['ESCAPE']:
                            expStop = True
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
                 pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
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

def timingCheckAndLog(ts,trialN):
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
nTrialsCorrectT2eachLag = np.zeros(len(possibleCue2lags)); nTrialsEachLag = np.zeros(len(possibleCue2lags))
nTrialsApproxCorrectT2eachLag = np.zeros(len(possibleCue2lags));

def do_RSVP_stim(cue1pos, cue2lag, proportnNoise,trialN):
    #relies on global variables:
    #   logging, bgColor
    #
    cuesPos = [] #will contain the positions of all the cues (targets)
    cuesPos.append(cue1pos)
    if task=='T1T2':
        cuesPos.append(cue1pos+cue2lag)
    cuesPos = np.array(cuesPos)
    letterSequence = np.arange(0,26)
    np.random.shuffle(letterSequence)
    correctAnswers = np.array( letterSequence[cuesPos] )
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #generating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
        (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)

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
    return letterSequence,cuesPos,correctAnswers, ts  
    
def handleAndScoreResponse(passThisTrial,responses,responsesAutopilot,task,letterSequence,cuesPos,correctAnswers):
    #Handle response, calculate whether correct, ########################################
    if autopilot or passThisTrial:
        responses = responsesAutopilot
    
    eachCorrect = np.zeros( len(correctAnswers) )
    eachApproxCorrect = np.zeros( len(correctAnswers) )
    posOfResponse = np.zeros( len(cuesPos) )
    responsePosRelative = np.zeros( len(cuesPos) )
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

    for i in range(len(cuesPos)): #print response stuff to dataFile
        #header was answerPos0, answer0, response0, correct0, responsePosRelative0
        print(cuesPos[i],'\t', end='', file=dataFile)
        answerCharacter = numberToLetter( letterSequence [cuesPos[i] ] )
        print(answerCharacter, '\t', end='', file=dataFile) #answer0
        print(responses[i], '\t', end='', file=dataFile) #response0
        print(eachCorrect[i] , '\t', end='',file=dataFile)   #correct0
        print(responsePosRelative[i], '\t', end='',file=dataFile) #responsePosRelative0

        correct = eachCorrect.all() 
        T1approxCorrect = eachApproxCorrect[0]
    return correct,eachCorrect,eachApproxCorrect,T1approxCorrect,passThisTrial,expStop
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

expStop=False; framesSaved=0
if doStaircase:
    #create the staircase handler
    useQuest = True
    if  useQuest:
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
    else:
        stepSizesLinear = [.2,.2,.1,.1,.05,.05]
        stepSizesLog = [log(1.4,10),log(1.4,10),log(1.3,10),log(1.3,10),log(1.2,10)]
        staircase = data.StairHandler(startVal = 0.1,
                                  stepType = 'log', #if log, what do I want to multiply it by
                                  stepSizes = stepSizesLog,    #step size to use after each reversal
                                  minVal=0, maxVal=1,
                                  nUp=1, nDown=3,  #will home in on the 80% threshold
                                  nReversals = 2, #The staircase terminates when nTrials have been exceeded, or when both nReversals and nTrials have been exceeded
                                  nTrials=1)
        print('created conventional staircase')
        
    if prefaceStaircaseTrialsN > len(prefaceStaircaseNoise): #repeat array to accommodate desired number of easyStarterTrials
        prefaceStaircaseNoise = np.tile( prefaceStaircaseNoise, ceil( prefaceStaircaseTrialsN/len(prefaceStaircaseNoise) ) )
    prefaceStaircaseNoise = prefaceStaircaseNoise[0:prefaceStaircaseTrialsN]
    
    phasesMsg = ('Doing '+str(prefaceStaircaseTrialsN)+'trials with noisePercent= '+str(prefaceStaircaseNoise)+' then doing a max '+str(staircaseTrials)+'-trial staircase')
    print(phasesMsg); logging.info(phasesMsg)
    
    #staircaseStarterNoise PHASE OF EXPERIMENT
    corrEachTrial = list() #only needed for easyStaircaseStarterNoise
    staircaseTrialN = -1; mainStaircaseGoing = False
    while (not staircase.finished) and expStop==False: #staircase.thisTrialN < staircase.nTrials
        if staircaseTrialN+1 < len(prefaceStaircaseNoise): #still doing easyStaircaseStarterNoise
            staircaseTrialN += 1
            noisePercent = prefaceStaircaseNoise[staircaseTrialN]
        else:
            if staircaseTrialN+1 == len(prefaceStaircaseNoise): #add these non-staircase trials so QUEST knows about them
                mainStaircaseGoing = True
                print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise)
                staircase.importData(100-prefaceStaircaseNoise, np.array(corrEachTrial))
                printStaircase(staircase, descendingPsycho, briefTrialUpdate=False, printInternalVal=True, alsoLog=False)
            try: #advance the staircase
                printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
                noisePercent = 100. - staircase.next()  #will step through the staircase, based on whether told it (addResponse) got it right or wrong
                staircaseTrialN += 1
            except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
                print('stopping because staircase.next() returned a StopIteration, which it does when it is finished')
                break #break out of the trials loop
        #print('staircaseTrialN=',staircaseTrialN)
        letterSequence,cuesPos,correctAnswers, ts  = do_RSVP_stim(cue1pos, cue2lag, noisePercent/100.,staircaseTrialN)
        numCasesInterframeLong = timingCheckAndLog(ts,staircaseTrialN)
        
        responseDebug=False; responses = list(); responsesAutopilot = list();
        expStop,passThisTrial,responses,responsesAutopilot = \
                    collectResponses(task,numRespsWanted,responseDebug=True)
        if not expStop:
            if mainStaircaseGoing:
                print('staircase\t', end='', file=dataFile)
            else: 
                print('staircase_preface\t', end='', file=dataFile)
             #header start      'trialnum\tsubject\ttask\t'
            print(staircaseTrialN,'\t', end='', file=dataFile) #first thing printed on each line of dataFile
            print(subject,'\t',task,'\t', round(noisePercent,2),'\t', end='', file=dataFile)
            correct,eachCorrect,eachApproxCorrect,T1approxCorrect,passThisTrial,expStop = (
                    handleAndScoreResponse(passThisTrial,responses,responsesAutopilot,task,letterSequence,cuesPos,correctAnswers) )
            #print('Scored response. expStop=',expStop) #debug
            print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
            core.wait(.06)
            if feedback: 
                play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
            print('staircaseTrialN=', staircaseTrialN,' noisePercent=',round(noisePercent,3),' T1approxCorrect=',T1approxCorrect) #debugON
            corrEachTrial.append(T1approxCorrect)
            if mainStaircaseGoing: 
                staircase.addResponse(T1approxCorrect, intensity = 100-noisePercent) #Add a 1 or 0 to signify a correct/detected or incorrect/missed trial
                #print('Have added an intensity of','{:.3f}'.format(100-noisePercent), 'T1approxCorrect =', T1approxCorrect, ' to staircase') #debugON
    #ENDING STAIRCASE PHASE

    if staircaseTrialN+1 < len(prefaceStaircaseNoise) and (staircaseTrialN>=0): #exp stopped before got through staircase preface trials, so haven't imported yet
        print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise[0:staircaseTrialN+1])
        staircase.importData(100-prefaceStaircaseNoise[0:staircaseTrialN], np.array(corrEachTrial)) 

    timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
    msg = ('prefaceStaircase phase' if expStop else '')
    msg += ('ABORTED' if expStop else 'Finished') + ' staircase part of experiment at ' + timeAndDateStr
    logging.info(msg); print(msg)
    printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
    #print('staircase.quantile=',round(staircase.quantile(),2),' sd=',round(staircase.sd(),2))
    threshNoise = round(staircase.quantile(),3)
    if descendingPsycho:
        threshNoise = 100- threshNoise
    threshNoise = max( 0, threshNoise ) #e.g. ff get all trials wrong, posterior peaks at a very negative number
    msg= 'Staircase estimate of threshold = ' + str(threshNoise) + ' with sd=' + str(round(staircase.sd(),2))
    logging.info(msg); print(msg)
    myWin.close()
    #Fit and plot data
    fit = None
    try:
        intensityForCurveFitting = staircase.intensities
        if descendingPsycho: 
            intensityForCurveFitting = 100-staircase.intensities #because fitWeibull assumes curve is ascending
        fit = data.FitWeibull(intensityForCurveFitting, staircase.data, expectedMin=1/26., sems = 1.0/len(staircase.intensities))
    except:
        print("Fit failed.")
    plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshCriterion)
    #save figure to file
    pylab.savefig(fileName+'.pdf')
    print('The plot has been saved, as '+fileName+'.pdf')
    pylab.show() #must call this to actually show plot
else: #not staircase
    noisePercent = defaultNoiseLevel
    phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials. Letters will be drawn with superposed noise of' + "{:.2%}".format(defaultNoiseLevel)
    print(phasesMsg); logging.info(phasesMsg)
    
    #myWin= openMyStimWindow();    myWin.flip(); myWin.flip();myWin.flip();myWin.flip()
    nDoneMain =0
    while nDoneMain < trials.nTotal and expStop==False:
        if nDoneMain==0:
            msg='Starting main (non-staircase) part of experiment'
            logging.info(msg); print(msg)
        thisTrial = trials.next() #get a proper (non-staircase) trial
        cue1pos = thisTrial['cue1pos']
        cue2lag = thisTrial['cue2lag']
        letterSequence,cuesPos,correctAnswers,ts  = do_RSVP_stim(cue1pos, cue2lag, noisePercent/100.,nDoneMain)
        numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)
        
        responseDebug=False; responses = list(); responsesAutopilot = list();
        expStop,passThisTrial,responses,responsesAutopilot = \
                    collectResponses(task,numRespsWanted,responseDebug=True)
        if not expStop:
            print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile
            print(nDoneMain,'\t', end='', file=dataFile)
            print(subject,'\t',task,'\t', round(noisePercent,3),'\t', end='', file=dataFile)
            correct,eachCorrect,eachApproxCorrect,T1approxCorrect,passThisTrial,expStop = (
                    handleAndScoreResponse(passThisTrial,responses,responsesAutopilot,task,letterSequence,cuesPos,correctAnswers) )
            print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
        
            numTrialsCorrect += correct #so count -1 as 0
            numTrialsApproxCorrect += eachApproxCorrect.all()
            numTrialsEachCorrect += eachCorrect
            numTrialsEachApproxCorrect += eachApproxCorrect
            cue2lagIdx = list(possibleCue2lags).index(cue2lag)
            nTrialsCorrectT2eachLag[cue2lagIdx] += eachCorrect[1]
            nTrialsApproxCorrectT2eachLag[cue2lagIdx] += eachApproxCorrect[1]
            nTrialsEachLag[cue2lagIdx] += 1
                
            if exportImages:  #catches one frame of response
                 myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
                 framesSaved +=1; core.wait(.1)
                 myWin.saveMovieFrames('exported/frames.mov')  
                 expStop=True
            core.wait(.1)
            if feedback: play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
            nDoneMain+=1
            
            dataFile.flush(); logging.flush()
            print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal) #' trials.thisN=',trials.thisN
            if (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
                 ( trials.nTotal*pctCompletedBreak/100. ) ==1):  #dont modulus 0 because then will do it for last trial
                    nextText.setText('Press "SPACE" to continue!')
                    nextText.draw()
                    progressMsg = 'Completed ' + str(nDoneMain) + ' of ' + str(trials.nTotal) + ' trials'
                    NextRemindCountText.setText(progressMsg)
                    NextRemindCountText.draw()
                    myWin.flip() # myWin.flip(clearBuffer=True) 
                    waiting=True
                    while waiting:
                       if autopilot: break
                       elif expStop == True:break
                       for key in event.getKeys():      #check if pressed abort-type key
                             if key in ['space','ESCAPE']: 
                                waiting=False
                             if key in ['ESCAPE']:
                                expStop = False
                    myWin.clearBuffer()
            core.wait(.2); time.sleep(.2)
        #end main trials loop
timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
msg = 'Finishing at '+timeAndDateStr
print(msg); logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials done='+ str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.error(msg)

if not doStaircase and (nDoneMain >0):
    print('Of ',nDoneMain,' trials, on ',numTrialsCorrect*1.0/nDoneMain*100., '% of all trials all targets reported exactly correct',sep='')
    print('All targets approximately correct in ',round(numTrialsApproxCorrect*1.0/nDoneMain*100,1),'% of trials',sep='')
    print('T1: ',round(numTrialsEachCorrect[0]*1.0/nDoneMain*100.,2), '% correct',sep='')
    if len(numTrialsEachCorrect) >1:
        print('T2: ',round(numTrialsEachCorrect[1]*1.0/nDoneMain*100,2),'% correct',sep='')
    print('T1: ',round(numTrialsEachApproxCorrect[0]*1.0/nDoneMain*100,2),'% approximately correct',sep='')
    if len(numTrialsEachCorrect) >1:
        print('T2: ',round(numTrialsEachApproxCorrect[1]*1.0/nDoneMain*100,2),'% approximately correct',sep='')
        print('T2 for each of the lags,',np.around(possibleCue2lags,0),': ', np.around(100*nTrialsCorrectT2eachLag / nTrialsEachLag,3), '%correct, and ',
                 np.around(100*nTrialsApproxCorrectT2eachLag/nTrialsEachLag,3),'%approximately correct')
   #print numRightWrongEachSpeedOrder[:,1] / ( numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1])   

logging.flush(); dataFile.close()
myWin.close() #have to close window if want to show a plot
#ADD PLOT OF AB PERFORMANCE?
