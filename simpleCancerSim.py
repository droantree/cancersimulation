# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 18:52:50 2016

@author: donal
"""
#
#Simulation explanation:
#  Based on the incidence rate parameter, cancer starts in a population according to a poisson process.
#  The cancer progresses according to a Gompertz model (i.e. the probability of the sufferer dying from it 
#     at any particular stage is modeled as a Gompertz distribution.) The distribution is specified
#     by providing the Median stage (i.e. number of days) and also the probability of death before half this
#     median. (See misc.py) i.e. MEDmort is such that CDF(MEDmort)=0.5 and PHALFmort = CDFmort(MEDmort/2)
#     In this model the two parameters are picked as follows:
#        - MEDmort will be picked from a uniform distribution from 60 to 700 (approx 2 months to 2 years)
#        - PHALFmort will be fixed at 0.02 (experiments suggest this as generating a reasonable shape)
#  The cancer is only diagnosed/noticed by the sufferer at some stage after it has developed. It is 
#     assumed that once it is noticed it is immediately diagnosed by a doctor. A more complex
#     simulation later can nodel the scenario where the sufferer has to make an appointment to be seen
#     by their doctor after noticing the cancer in order to have it diagnosed.
#  The probability of noticing the cancer follows a Gompertz model which is related to the progress model
#     as follows: 
#     The Median number of days is picked from a uniform distribution from CDFINVmort(0.01) to MEDmort
#     The ProbHalfMedian is picked from a uniform distribution from 0.02 to 0.2
#  This is a discrete simulation, progressing on a day-to-day basis.
#  The term "stage" refers to the number of days since a cancer started in a sufferer.
#  There are a fixed number of treatment appointment slots per day and a sufferer is always booked
#     into the next available slot when cancer is diagnosed and sufferers never miss or
#     postpone their appointments.
#  A sufferer always survives until their appointment but, of course, the prob of successful treatment
#     decreases even to zero.
#  When a suffer is treated, the treatment is immediately successful or they die immediately, i.e.
#     this simulation does not model time to recover or time during which the cancer progresses to its
#     terminal stage.
#  The probability of the treatment being successful is based simply on a probability derived from the 
#     stage in the mortality model as follows: at stage(day) x, CDFmort(x) = p, then the prob of
#     successful treatment is 1-p.
#  The incidence rate of cancer is relatively low so the simulation does not model the decrease in
#     the population size due to cancer deaths.

import numpy as np
import misc.py

#Simulation parameters
POPULATION = 1000000
SLOTS_PER_DAY = 20  #number of appointment slots that can be allocated each day
DAYS_TO_RUN = 365 * 5  #5 years
CANCER_START_DAILY_INCIDENCE_RATE = float(1) / (2 * 70 * 365)  #corresponds to person having a 50/50 chance of developing cancer in their life, avg lifespan 70 years
AVERAGE_UNTREATED_LIFE_EXPECTANCY_DAYS = 365  #corresponds to suffers' expected days of life when cancer untreated

#Status values
STATUS_NOT_TREATED = "NT"
STATUS_TREATMENT_SUCCEEDED = "SC"
STATUS_TREATMENT_FAILED = "FL"

#Simulation tracking variables
class Sufferer:
    def __init__(self, today):
        self.dayCancerStarted = today
        self.appt = None #when created the cancer has not been diagnosed and so there is no appointment
        self.status = STATUS_NOT_TREATED
        self.mortalityParams = 

    def cancerStage(self, day):
        return day - self.dayCancerStarted        
        
    def progressOneDay(self, today):
        #3 cases - no appt yet (because cancer not noticed)
        #        - waiting for an appointment
        #        - had an appt and either success or failure
        cancerStageToday = self.cancerStage(today)
        if self.appt == None:
            suffererNoticesCancerToday = isNoticed(cancerStageToday)
            if suffererNoticesCancerToday:
                self.appt = Model.apptSchedule.getNextApptSlot(today)
            #Note: if the sufferer does not notice the cancer there is no progress to process
        elif today < self.appt:
            pass #sufferer continues to wait for their appointment
        elif today >= self.appt:
            if isTreatmentSuccessful(cancerStageToday):
                self.status = STATUS_TREATMENT_SUCCEEDED
            else:
                self.status = STATUS_TREATMENT_FAILED
    
    def isStatusSuccess(self):
        return self.status == STATUS_TREATMENT_SUCCEEDED

    def isStatusFailed(self):
        return self.status == STATUS_TREATMENT_FAILED
        
    def hasBeenTreated(self):
        return self.status <> STATUS_NOT_TREATED
######## End of class Sufferer
        

class ApptSchedule:
    def __init__(self):    
        self.nextApptDay = 1
        self.apptsRemainingNextApptDay = SLOTS_PER_DAY #this should never get down to zero
        
    def resetNextApptDayToDay(self, day):
        self.nextApptDay = day
        self.apptsRemainingNextApptDay = SLOTS_PER_DAY
        
    def decrementSlotsAvailableNextApptDay(self):
        self.apptsRemainingNextApptDay -= 1
        if self.apptsRemainingNextApptDay == 0:
            self.resetNextApptDayToDay(self.nextApptDay + 1)
        
    def getNextApptSlot(self, today):
        if today > self.nextApptDay:
            self.resetNextApptDayToToday(today)
        nextSlotDay = self.nextApptDay
        self.decrementSlotsAvailableNextApptDay()
        return nextSlotDay
######## End of class ApptSchedule
        
    
class Model:
    def __init__(self):
        self.sufferers = []  #a list of Sufferer objects
        self.today = 0
        self.apptSchedule = ApptSchedule()
    
    def progressToNextDay(self):
        self.today += 1
        #create new sufferers randomly
        numberOfNewCancerSuffers = numberOfNewCancerStartsToday()
        self.createNewSuffers(numberOfNewCancerSuffers) 
        #go through all sufferers and "progress" them to today
        for sufferer in self.sufferers:
            . .  . . . . .

    def createNewSuffers(self, numberOfNewSufferers):
        for i in range(numberOfNewSufferers):
            newSufferer = Sufferer(self.today)
            self.sufferers.append(newSufferer)
            
######## End of class Model

def pickRandomMortalityParams():
    MEDmort = float(np.random.randint(60, 700))
    PHALFmort = 0.02
    return gompertzParams(MEDmort, PHALFmort)

def numberOfNewCancerStartsToday():
    #Assume poisson process with mean rate*population.
    averageStartsPerDay = CANCER_START_DAILY_INCIDENCE_RATE / POPULATION
    return np.random.poisson(averageStartsPerDay)

def pickRandomTF(probOfTrue):
    randomFrom0To1 = np.random.uniform()
    return randomFrom0To1 <= probOfTrue
    
def isTreatmentSuccessful(stageTreated):
    #Random True/False depending on the probability of successful treatment given this stage.    
    #The probability that treatment at the given stage will be ultimately successful.
    #Should reflect the real-world disimproved prognosis as treatment is given later and later.
    # SIMPLE MODEL - Prob success at stage 1 is 1 and is 0 at stage averageUntreatedLifeExpectancyDays and prob decreases linearly.
    #                If stage is beyond averageUntreatedLifeExpectancyDays then prob is 0.
    if stageTreated >= AVERAGE_UNTREATED_LIFE_EXPECTANCY_DAYS:
        return False
    elif stageTreated <= 1:
        return True
    else:
        probOfFailure = float(stageTreated) / AVERAGE_UNTREATED_LIFE_EXPECTANCY_DAYS
        probOfSuccess = 1 - probOfFailure
        return pickRandomTF(probOfSuccess)

def isNoticed(stage):
    #Random True/False depending on the probability of noticing the cancer given this stage.    
    #The probability that cancer at the given stage is noticed/diagnosed (that day).
    # SIMPLE MODEL - Prob of noticing at stage 1 is 0 and is 1 at stage averageUntreatedLifeExpectancyDays and prob increases linearly.
    #                If stage is beyond averageUntreatedLifeExpectancyDays then prob is 1.
    #
    #MUST FIX THIS UP - Prob of noticing on any particular day is much less!
    #
    if stage >= AVERAGE_UNTREATED_LIFE_EXPECTANCY_DAYS:
        return False
    elif stage <= 1:
        return False
    else:
        probOfNotice = float(stage) / AVERAGE_UNTREATED_LIFE_EXPECTANCY_DAYS
        return pickRandomTF(probOfNotice)

#Finally, actually run the model:
simModel = Model();
for day in range(DAYS_TO_RUN):
    simModel.progressToNextDay()
