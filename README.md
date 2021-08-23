Attentional Blink implemented with [Psychopy](https://github.com/psychopy/psychopy)
============================
MIT license, like CC-BY for code which means do whatever you want with it, with an attribution to the author.

Main version **AB.py** includes optional noise staircase, finding noise level to titrate T1 approx correct to a particular level.

**ltrsNoiseQuestDemo.py** is a playground for how the noise and staircase work. 

Used in [Cellini et al. (2015)](http://dx.doi.org/10.3758/s13414-015-0912-7) and with Agosta, Battelli, & Goodbourn on left parietal lobe patients.

###Empirical background
Martini AB data were the averages of 20 undergrads. Each contributed 4 consecutive blocks of 100 trials, total time about 35 minutes. The parameters were identical to Vul 2008, 
with a duticycle of 90ms (~11 Hz) and each character shown for 3 frames (33 ms at 90 Hz framerate). Note that in those conditions the bottom of AB at lags 2 and 3 is effectively at chance, so there may be a floor effect there.

In experiment 1b I used 15Hz streams, 2 blocks of 100 trials, and that takes roughly 12-15 minutes.
There is some learning, Martini  measured it in experiment 1a with repeat subjects (graph attached), so you should check whether your effects would be washed out by this. 
Also, experiment 1b was run with T1 fixed, i.e. the cue was always in the midstream position.

For detailed analysis of serial position errors, see Goodbourn & Holcombe (2014).  Journal of Experimental Psychology: Human Perception & Performance

####Instructions

####Optional staircase phase

STAIRCASE CURRENTLY DOES NOT CHANGE THE CUE1POS AND CUE2 LAG FROM TRIAL TO TRIAL. **ALEX FIX**!

**Motivation**: Our parietal patients had poor T1 performance of around 58% approximately (Vul et al.) correct. Their attentional blink curve looks different from the elderly controls, but the lower T1 performance is a confound. 

To reduce the T1 performance of a subject (elderly control in our case), we add noise to the letters. To determine the noise level needed to reduce performance to 58% correct, run AB.py and choose the staircase experiment. You are then prompted to modify the staircase parameters, if you like, before the staircase is run and the results plotted at the end, like this: 
![staircase plot](https://github.com/alexholcombe/attentional-blink/blob/master/example_staircase_plot.jpg "staircase plot")
The threshold printed at the top of the plot (and printed at the end of the .log file) can then be used for the main experiment. 

Because the participant may be confused about the task at first, you ought to give her some practice trials first by running this and pressing ESCAPE when you think she has had enough, and ignoring the results until you run it again.

####Main AB experiment

Run AB.py and choose "main" experiment. If you want noise on the letters (for example the value suggested by the staircase), change the percent noise from the default value of 0. Data in long format is in the <subject details>.txt file. A copy of the code as it was when executed is in the <subject details>.py file. Diagnostics are in the .log file.

Summary of results are printed in output window.


######Staircase piloting notes
Alex with glasses off to simulate elderly, targeted 90% correct with staircase.
Started with 20 trials of noise= [ 2  2  5  5 10 80 80 80  2  2  5  5 10 80 80 80] then a max 20-trial staircase followed by 25 trials at that noise level. Yielded 85% approx correct for T1.

#######History

Jan 2012 started implementing attentional blink task. Started git repository on 5 November 2014 with non-git AB_addNoise_QUEST2.py
