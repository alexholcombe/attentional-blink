from psychopy import data
import numpy as np
#my data
x=np.array( [5.0, 10.0, 20.0, 50.0, 70.0, 80.0, 95.0])
y=np.array(  [0.4, 0.4, 0.4, 0.57, 1.0, 1.0, 1.0] ) #good

expectedMin =0
try:
    data.FitWeibull(x,y,expectedMin=expectedMin)
    print('Fit succeeded on my 1st dataset')
except:
    print('Fit failed on my 1st dataset')
    
#my data
x=np.array( [5.0, 10.0, 20.0, 50.0, 70.0, 80.0, 95.0])
y=np.array(  [0.0, 0.0, 0.0, 0.57, 1.0, 1.0, 1.0] ) #bad FIT FAILS. Doesnt seem to like zeros

expectedMin =0
try:
    data.FitWeibull(x,y,expectedMin=expectedMin)
    print('Fit succeeded on my 2nd dataset')
except:
    print('Fit failed on my 2nd dataset')

#JWP JND_staircase_exp data
x=np.array( [0.0, 1.0, 2.0, 3.0, 4.0, 12.0, 20.0])
y=np.array([ 0.4, 0.63, 0.8, 0.92, 1.0, 1.0, 1.0])
expectedMin = 0
try:
    data.FitWeibull(x,y,expectedMin=expectedMin)
    print('Fit succeeded on Jon''s data')
except:
    print('Fit failed on Jon''s data')

#plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshVal=0.5)

