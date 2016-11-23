# -*- coding: utf-8 -*-
'''
The standard/simple Gompertz model has 2 parameters, eta and b, and CDF F given by:

F(x) = 1 - exp( -eta * ( exp (b*x) - 1 ) )

Given a sizable mortality dataset you could calibrate b and eta. Instead, I am going
to look for values of eta and b that give me a realistic-looking distribution.
I will pick the following two values which will determine the model (parameters):
M - the median value of the distribution, i.e. 
F(0.5) = M                                        [1]
ProbHalfM - the probability of X being less than half the median, i.e. 
ProbHalfM = F(M/2)                                [2]

So, ln(1-ProbHalfM) = -eta * (exp(b*M/2) - 1)
    ==> eta = ln(1-ProbHalfM) / (1 - exp(b*M/2))  [3]

Using equations [1] and [2] and the definition of F we can relate b and eta to M and ProbHalfM
as follows.

Let K = exp( b*M/2 )                              [4]
so b = 2*ln(K)/M                                  [5]

Let L = ln(1-ProbHalfM) / ln(0.5)                 [6]

Note: ProbHalfM < 0.5 by [2]
      ==> 1-ProbHalfM > 0.5
      ==> L > 1

K = (1 + sqrt(4*L^2 - 4*L + 1)) / (2*L)           [7]
Note: K is root of quadratic but the other root will be negative since L>1 so can be ignored.

So, calculate as follows:
1. From [6], calculate L
2. From [7], calculate K
3. From [5], calculate b 
4. From [3], calculate eta

Knowing b and eta allows us to calculate F(x) for any x.
'''

import numpy as np
import matplotlib.pyplot as plt

np.set_printoptions(suppress=True)

###### Gompertz-related functions (see notes above) ###########

def gompertzParams(M, ProbHalfM):
    #returns a dictionary with keys b and eta
    L = np.log(1.0 - ProbHalfM) / np.log(0.5)
    K = (1 + np.sqrt(4.0*np.power(L,2) - 4.0*L + 1.0)) / (2.0*L)
    b = (2.0 * np.log(K)) / M
    eta = np.log(1.0-ProbHalfM) / (1 - np.exp(b*M/2.0))
    return {"b": b, "eta": eta}
    
def CDFGompertz(gParams, x):
    b = gParams["b"]
    eta = gParams["eta"]
    return 1.0 - np.exp(-eta * (np.exp(b*x) - 1))
    
def CDFInverseGompertz(gParams, p):
    b = gParams["b"]
    eta = gParams["eta"]
    inner = 1 - np.log(1-p)/float(eta)
    return np.log(inner) / float(b)
###### END OF: Gompertz-related functions ###########

###### Other stats-related functions ###########
def ProbDieBeforeT2GivenSurviveUntilTime1(time1, time2, gParams):
    # basically P(T <= time2 | T > time1) which is
    # (F(time2) - F(time1)) / (1 - F(time1))
    # where F is the CDF
    # b is the Gompertz parameter which should be calculated and passed into this function
    return (CDFGompertz(gParams, time2) - CDFGompertz(gParams, time1)) / (1 - CDFGompertz(gParams, time1))

def pickRandomTF(probOfTrue):
    randomFrom0To1 = np.random.uniform()
    return randomFrom0To1 <= probOfTrue
###### END OF: Other stats-related functions ###########

########## Test Gompertz #################    

'''
Median = 20 #equal chance of surviving to this number of days as not
ProbHalfMedian = 0.1

gParams = gompertzParams(Median, ProbHalfMedian)

for i in range(51):
    print str(i) + "%: " + str(CDFInverseGompertz(gParams, i/100.0))

for i in range(100):
        probDie = ProbDieBeforeT2GivenSurviveUntilTime1(1,2, gParams)
        if pickRandomTF(probDie):
            print "die"
        else:
            print "---"

#for day in range(Median*2):
#    print "day " + str(day) + ": " + str(CDFGompertz(gParams, day))

print "gParams=" + str(gParams)
print CDFGompertz(gParams, Median)

sumbins = np.zeros(Median*2)
sumsqrbins = np.zeros(Median*2)
iterations = 40
for i in range(iterations):
    bins = np.zeros(Median*2)
    for testSubject in range(1000):
        for day in range(Median*2):
            probDie = ProbDieBeforeT2GivenSurviveUntilTime1(day, day+1, gParams)
            if pickRandomTF(probDie):
                bins[day] += 1
                break
    sumbins += bins
    sumsqrbins += bins**2
    print "iteration: " + str(i)
means = sumbins / float(iterations)
stdevs = np.sqrt((sumsqrbins - (sumbins**2)/float(iterations)) / float(iterations))
        
print means
print np.cumsum(means)
print stdevs
print "sum bins: " + str(sum(bins))
print "sum 30 bins: " + str(sum(bins[1:30]))
print "sum 15 bins: " + str(sum(bins[1:15]))
'''
########## END OF: Test Gompertz ###########