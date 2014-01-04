#!/usr/bin/python

from __future__ import division
import os
import pandas
import struct
from io import open
from pandas import DataFrame, Series, rolling_mean
import subprocess
from datetime import datetime,date,timedelta
import matplotlib.pyplot as plt

from interfaces import *

#from interfaces import DataFeeder, Algorithm

class GpwDataFeeder( DataFeeder ):
    
    def __init__(self, startDate, endDate, gpwName):
        super(GpwDataFeeder,self).__init__(startDate, endDate)
        self.gpwName = gpwName
        self.df = pandas.read_csv('CCC.mst')
#        print self.df.shape
        self.currPos = self.findStartPoint()
	#print p[:2]
	#print p[:2]['<VOL>']
	#print p[:2]['<OPEN>']

    def findStartPoint(self):
        shape = self.df.shape
#        print self.df[(shape[0]-1):]['<DTYYYYMMDD>']
#        print self.df.iloc[0]['<DTYYYYMMDD>']        
        i = 0        
        while i < shape[0]:
            curDate = datetime.strptime(str(self.df.iloc[i]['<DTYYYYMMDD>']),'%Y%m%d')
            diff = curDate - datetime.combine(self.startDate, datetime.min.time())
            if diff >= timedelta(0):
                break
            i = i+1
        return i
    
    def debugKK(self, level, txt):
        if (level > 0):
            print txt
        
                                        
    def getData(self):
#        self.debugKK(1,str(self.currPos >= self.df.shape[0]));
        if self.currPos >= self.df.shape[0]:
            return None
        curDate = datetime.strptime(str(self.df.iloc[self.currPos]['<DTYYYYMMDD>']),'%Y%m%d')
        diff = curDate - datetime.combine(self.endDate, datetime.min.time());
#        self.debugKK(1,str(self.currPos >= self.df.shape[0]));        
        if diff > timedelta(0):
            return None
        self.currPos += 1
        return self.df.iloc[self.currPos-1];
        
#        self.debugKK(0,'df poz ' + str(self.dfPosition + 1) + ' size ' + str(self.df.shape[0]))
#        if (self.dfPosition + 1) == self.df.shape[0]:
#            return self.newHour()
#        else:
#            self.dfPosition += 1
#            return self.df.iloc[self.dfPosition]
        return
          
          
class RolingMeanAlgorithm( Algorithm ):
    
    def __init__(self, smallAvg, bigAvg):
        self.df = Series()
        self.smallAvg = smallAvg
        self.bigAvg = bigAvg
        self.was = 0
        
    
#    def getInputSettings( self ):
#        """metoda ta zwracalaby obiekt InputSettings, ktory to zawieralby 
#        informacje odnosnie tego jakie wymogi musza spelniac danewejsciowe,
#        na razie wydaje mi sie ze moze to byc:
#        a) minimalny zakres danych
#        b) skok danych - odstep czasowy miedzy poszczegolnymi wartosciami
#        x) pewnie masz pomysly na wiecej parametrow"""	
#        raise NotImplementedError( "Should have implemented this" )

    def getBuySignals( self, measurement, colName ):
        """na wejsciu data frame o zadanych przez InputSettings parametrach,
        na wyjsciu 0,1,-1 kiedy kupowac z kierunkiem - nie wiem czy bedziemy
        mieli takie algorytmy co beda w wyniku dawac sygnaly -1,1?
        """
        #print (self.df)
        self.df = self.df.append(Series(measurement[colName],index = ['a']))
        #print measurement.name
        #sys.exit(1)
        if self.df.shape[0] == self.bigAvg:
            curBig = rolling_mean(self.df, self.bigAvg)
            curSmall = rolling_mean(self.df[(self.bigAvg-self.smallAvg):], self.smallAvg)
#            print "1=========================="
#            print curBig[-1]
#            print curSmall[-1]
            
            if curBig[-1] < curSmall[-1]:
                self.df = self.df[1:]
                #return [self.getReturn(1), measurement.name]
                return self.getReturn(1)
            else:
                self.df = self.df[1:]
                #return [self.getReturn(-1), measurement.name]
                return self.getReturn(-1)
        else:
            return 0

    def getReturn(self, curVal):
        if self.was == 0:
            self.was = curVal
            return curVal
        elif self.was == -1:
            if curVal == -1:
                return 0
            else:
                self.was = 1
                return 1
        elif self.was == 1:
            if curVal == 1:
                return 0
            else:
                self.was = -1
                return -1
        
        return 0
            
        
        
          
                
feeder = GpwDataFeeder(date(2012, 1, 1),date(2012, 12, 31), 'CCC')

broker = Broker()
wallet = Wallet(25000, BuyForOneTenthOfWalletBuyStrategy(), SellIfUpBy10OrDownBy5SellStrategy(), broker)
alg = RolingMeanAlgorithm(5,20)

sim = Simulator(wallet, alg, feeder)

sim.run()

exit

#dataFrame = DataFrame()
#signals = Series()
##
#curFeed = feeder.getData()
##lastFeed = curFeed
#while curFeed is not None:
##    lastFeed = curFeed
#    dataFrame = dataFrame.append([curFeed])
##    #print curFeed
#    signal = alg.getBuySignals(curFeed, '<CLOSE>')
#    signals = signals.append(Series(signal[0], index = [signal[1]]))
##    curFeed = feeder.getData()
#
#    curFeed = feeder.getData()
#    
##print lastFeed
##    dataFrame = dataFrame.append([curFeed])
##    #print curFeed
##    signal = alg.getBuySignals(curFeed)
##    signals = signals.append(Series(signal[0], index = [signal[1]]))    
##    curFeed = feeder.getData()
##
#dataFrame['<CLOSE>'].plot();
###rolling_mean(dataFrame['ask'], 20).plot()
###rolling_mean(dataFrame['ask'], 5).plot()
###print rolling_mean(dataFrame['ask'], 20)[20:30]
###print rolling_mean(dataFrame['ask'], 5)[20:30]
###print signals[20:30]
#signals.plot()
#plt.show()

