# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 23:22:32 2016

@author: donal
"""
import math

ETA = 0.018

print b

halflife = 365 / 2 #equal chance of surviving to this number of days as not

def GompertzBParam(halflife):
    inner = -(math.log(0.5) / eta)
    return (1.0/6.0*31) * (1 + math.log(inner))    

def CDFGompertz(x, b):
    power = -ETA*(math.exp(b*x-1))    
    return 1 - math.exp(power)

def Prob    