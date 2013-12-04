#!/usr/bin/python

from __future__ import division
import os
import pandas
import struct
from io import open
from pandas import DataFrame, Series, rolling_mean
import subprocess
from datetime import datetime,date
import matplotlib.pyplot as plt

from interfaces import DataFeeder, Algorithm

class GpwDataFeeder( DataFeeder ):
    
    def __init__(self, startDate, endDate, gpwName):
        super(GpwDataFeeder,self).__init__(startDate, endDate)
        self.gpwName = gpwName
	self.df = pandas.read_csv('CCC.mst')
	#print p[:2]
	#print p[:2]['<VOL>']
	#print p[:2]['<OPEN>']

    def findStartPoint(self):
	if (self.startDate )
	#while datetime.datetime.strptime(str(self.df[:i]['<DTYYYYMMDD>'][0]), '%Y%m%d')-startDate < datetime.timedelta(0):
        #        i = i + 1;   

    
    def debugKK(self, level, txt):
        if (level > 0):
            print txt
        
                                        
    def getData(self):
        self.debugKK(0,'df poz ' + str(self.dfPosition + 1) + ' size ' + str(self.df.shape[0]))
        if (self.dfPosition + 1) == self.df.shape[0]:
            return self.newHour()
        else:
            self.dfPosition += 1
            return self.df.iloc[self.dfPosition]
          
          
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

    def getBuySignals( self, measurement ):
        """na wejsciu data frame o zadanych przez InputSettings parametrach,
        na wyjsciu 0,1,-1 kiedy kupowac z kierunkiem - nie wiem czy bedziemy
        mieli takie algorytmy co beda w wyniku dawac sygnaly -1,1?
        """
        #print (self.df)
        self.df = self.df.append(Series(measurement['ask'],index = ['a']))
        #print measurement.name
        #sys.exit(1)
        if self.df.shape[0] == 20:
            curBig = rolling_mean(self.df, self.bigAvg)
            curSmall = rolling_mean(self.df[(self.bigAvg-self.smallAvg):], self.smallAvg)
#            print "1=========================="
#            print curBig[-1]
#            print curSmall[-1]
            
            if curBig[-1] < curSmall[-1]:
                
                #print "128=========================="
                self.df = self.df[1:]
                return [128,measurement.name]
            else:
                #print "129=========================="
                self.df = self.df[1:]
                return [130,measurement.name]
        else:
            return [129,measurement.name]

        
        
          
                
feeder = GpwDataFeeder(date(2012, 1, 1),date(2013, 1, 1), 'CCC')

#broker = Broker()
#wallet = Wallet(25000, BuyForOneTenthOfWalletBuyStrategy(), SellIfUpBy10OrDownBy5SellStrategy(), broker)
alg = RolingMeanAlgorithm(5,20)

#sim = Simulator(date(2012, 1, 1), date(2012, 1, 2), wallet, alg, feeder)



#dataFrame = DataFrame()
#signals = Series()
#
#curFeed = feeder.getData()
#while curFeed is not None:
#    dataFrame = dataFrame.append([curFeed])
#    #print curFeed
#    signal = alg.getBuySignals(curFeed)
#    signals = signals.append(Series(signal[0], index = [signal[1]]))    
#    curFeed = feeder.getData()
#
#dataFrame['ask'].plot();
##rolling_mean(dataFrame['ask'], 20).plot()
##rolling_mean(dataFrame['ask'], 5).plot()
##print rolling_mean(dataFrame['ask'], 20)[20:30]
##print rolling_mean(dataFrame['ask'], 5)[20:30]
##print signals[20:30]
#signals.plot()
#plt.show()

