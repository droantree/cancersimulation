# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 23:22:32 2016

@author: donal
"""
import numpy as np

ETA = 0.005  #0.018

def pickRandomTF(probOfTrue):
    randomFrom0To1 = np.random.uniform()
    return randomFrom0To1 <= probOfTrue

def GompertzBParam(halflife):
    inner = 1 - (np.log(0.5) / ETA)
    return (1.0/halflife) * np.log(inner)

def CDFGompertz(x, b):
    power = -ETA*(np.exp(b*x)-1)    
    return 1 - np.exp(power)

def ProbDieBeforeT2GivenSurviveUntilTime1(time1, time2, b):
    # basically P(T <= time2 | T > time1) which is
    # (F(time2) - F(time1)) / (1 - F(time1))
    # where F is the CDF
    # b is the Gompertz parameter which should be calculated and passed into this function
    return (CDFGompertz(time2, b) - CDFGompertz(time1, b)) / (1 - CDFGompertz(time1, b))

halflife = 60 / 2 #equal chance of surviving to this number of days as not

b = GompertzBParam(halflife)
print "b=" + str(b)
print CDFGompertz(30.0, b)

'''
for day in range(1, 2*halflife):
    probDyingThisDay = ProbDieBeforeT2GivenSurviveUntilTime1(day-1, day, b)
    print "Day {}: {}".format(day, probDyingThisDay)
'''
bins = np.zeros(60)
for testSubject in range(1000):
    for day in range(halflife*2):
        probDie = ProbDieBeforeT2GivenSurviveUntilTime1(day, day+1, b)
        if pickRandomTF(probDie):
            bins[day] += 1
            break
        
print bins

        