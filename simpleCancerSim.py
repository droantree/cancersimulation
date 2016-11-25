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
import misc as gp
#import matplotlib.pyplot as plt

#Simulation parameters
POPULATION = 500000
SLOTS_PER_DAY = 2  #number of appointment slots that can be allocated each day
DAYS_TO_RUN = 365 * 5  # years
CANCER_START_DAILY_INCIDENCE_RATE = float(1) / (2 * 70 * 365)  #corresponds to person having a 50/50 chance of developing cancer in their life, avg lifespan 70 years

#Status values
STATUS_NOT_TREATED = "NT"
STATUS_TREATMENT_SUCCEEDED = "SC"
STATUS_TREATMENT_FAILED = "FL"

#Simulation tracking variables
class Sufferer:
    def __init__(self, today, apptSchedule):
        self.apptSchedule = apptSchedule
        self.dayCancerStarted = today
        self.appt = None #when created the cancer has not been diagnosed and so there is no appointment
        self.status = STATUS_NOT_TREATED
        MEDmort = float(np.random.randint(60, 700))
        PHALFmort = 0.02
        self.mortalityParams = gp.gompertzParams(MEDmort, PHALFmort)        
        MEDnotice = randomUniformFloat(gp.CDFInverseGompertz(self.mortalityParams, 0.01), MEDmort)
        PHALFnotice = randomUniformFloat(0.02, 0.2)
        self.noticingParams = gp.gompertzParams(MEDnotice, PHALFnotice)

    def cancerStage(self, day):
        return day - self.dayCancerStarted        
        
    def progressOneDay(self, today, simResults):
        #3 cases - no appt yet (because cancer not noticed)
        #        - waiting for an appointment
        #        - had an appt and either success or failure
        cancerStageToday = self.cancerStage(today)
        if self.appt == None:
            suffererNoticesCancerToday = self.isNoticed(cancerStageToday)
            if suffererNoticesCancerToday:
                self.appt = self.apptSchedule.getNextApptSlot(today)
                #print "appt day=" + str(self.appt) + ", today=" + str(int(today))
                waitingDays = self.appt - today
                simResults.addApptSet(waitingDays, cancerStageToday + waitingDays)
            #Note: if the sufferer does not notice the cancer there is no progress to process
        elif today < self.appt:
            pass #sufferer continues to wait for their appointment
        elif today >= self.appt:
            if self.isTreatmentSuccessful(cancerStageToday):
                self.status = STATUS_TREATMENT_SUCCEEDED
            else:
                self.status = STATUS_TREATMENT_FAILED
    
    def isNoticed(self, cancerStageToday):
        cancerStageYesterday = cancerStageToday -1;
        probNoticing = gp.ProbEventBeforeT2GivenNoEventBeforeTime1(cancerStageYesterday, cancerStageToday, self.noticingParams)
        return pickRandomTF(probNoticing)        
        
    def isTreatmentSuccessful(self, cancerStageToday):
        probTreatmentSuccessful = 1 - gp.CDFGompertz(self.mortalityParams, cancerStageToday)
        return pickRandomTF(probTreatmentSuccessful)
    
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
            self.resetNextApptDayToDay(today)
        nextSlotDay = self.nextApptDay
        self.decrementSlotsAvailableNextApptDay()
        #print "(Slots per day=" + str(int(SLOTS_PER_DAY)) + ") Next slot on day=" + str(int(today)) + ", next appt day=" + str(int(self.nextApptDay)) + ", appts remaining next day=" + str(int(self.apptsRemainingNextApptDay))
        return nextSlotDay
######## End of class ApptSchedule
        
    
class Model:
    def __init__(self, simResults):
        self.sufferers = []  #a list of Sufferer objects
        self.today = 0
        self.apptSchedule = ApptSchedule()
        self.simResults = simResults
    
    def progressToNextDay(self):
        self.today += 1
        #create new sufferers randomly
        numberOfNewCancerSuffers = numberOfNewCancerStartsToday()
        self.createNewSuffers(numberOfNewCancerSuffers) 
        #go through all sufferers and "progress" them to today
        sufferersTreated = [] #record those sufferers that have been treated so they can be removed later
        for sufferer in self.sufferers:
            sufferer.progressOneDay(self.today, self.simResults)
            if sufferer.hasBeenTreated():
                sufferersTreated.append(sufferer) #don't remove a sufferer from self.sufferers here because that would interfere with the for loop 
                if sufferer.isStatusFailed():
                    self.simResults.addDeath(self.today)
                else:
                    self.simResults.addCure(self.today)
        for sufferer in sufferersTreated:
            self.sufferers.remove(sufferer)

    def createNewSuffers(self, numberOfNewSufferers):
        for i in range(numberOfNewSufferers):
            newSufferer = Sufferer(self.today, self.apptSchedule)
            self.sufferers.append(newSufferer)
            
######## End of class Model

class ModelResults:
    def __init__(self):
        self.deaths = np.zeros(DAYS_TO_RUN + 1)
        self.cured = np.zeros(DAYS_TO_RUN + 1)
        #from these next 3 we can calculate avg days to wait for an appt and avg stage when treated
        self.apptsWaitingDaysTotal = 0
        self.apptsTotal = 0
        self.treatmentStageTotalDays = 0
        
    def addDeath(self, day):
        self.deaths[day] += 1
        
    def addApptSet(self, daysToWait, stageAtAppt):
        self.apptsWaitingDaysTotal += daysToWait
        self.treatmentStageTotalDays += stageAtAppt
        self.apptsTotal += 1

    def addCure(self, day):
        self.cured[day] += 1
        
    def avgApptWaitDays(self):
        if self.apptsTotal == 0:
            return "--"
        else:
            return float(self.apptsWaitingDaysTotal) / float(self.apptsTotal)

    def avgStageTreated(self):
        if self.apptsTotal == 0:
            return "--"
        else:
            return float(self.treatmentStageTotalDays) / float(self.apptsTotal)


def numberOfNewCancerStartsToday():
    #Assume poisson process with mean rate*population.
    averageStartsPerDay = CANCER_START_DAILY_INCIDENCE_RATE * POPULATION
    return np.random.poisson(averageStartsPerDay)

def pickRandomTF(probOfTrue):
    randomFrom0To1 = np.random.uniform()
    return randomFrom0To1 <= probOfTrue
    
def randomUniformFloat(min, max):
    return np.random.random_sample() * (max - min) + min

#Finally, actually run the model:
print "{:>10}  {:>10}  {:>10}  {:>10}".format("slots", "deaths", "avg waits", "avg stage")
for SLOTS_PER_DAY in reversed(range(5, 16)):
    simResults = ModelResults();
    simModel = Model(simResults);
    for day in range(DAYS_TO_RUN):
        simModel.progressToNextDay()
    deaths = int(np.sum(simResults.deaths))
    print "{:>10}  {:>10}  {:>10.2f}  {:>10.2f}".format(SLOTS_PER_DAY, deaths, simResults.avgApptWaitDays(), simResults.avgStageTreated())
    
