#!/usr/bin/python

from __future__ import division
import os

import struct
from io import open
from pandas import DataFrame, Series, rolling_mean
import subprocess
from datetime import datetime,date
import matplotlib.pyplot as plt

from interfaces import DataFeeder, Algorithm


def processBinFile(infile,dateWithoutMilisec):

#	d = {'one' : Series([1., 2., 3.])}
#	return DataFrame(d)
	chunksize = 20
	
	#print("Processing hour: " + infile[:2])
	filesize = os.path.getsize(infile)
	if filesize > 0 & filesize%chunksize==0:
		f = open(infile, "rb")
	else:
		print "%s is corrupted or doesn't exist" % infile
		return None

  	#test if the file is valid pkzip file
	#if zipfile.is_zipfile(infile):
	#print "Loading %s" % infile
	unpacked_ticks = f.read()
	index=0

	ts=[]
	ask=[]
	bid=[]
	askV=[]
	bidV=[]
	
	
	# Processing binary file and extracting values
	for n in xrange(0, filesize, chunksize):	# reading file in chunks
		s = unpacked_ticks[index:index+chunksize]
		L1, L2, L3, L4, L5 = struct.unpack(">lllff", s)
		#Timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(L1/1000)) + '.' + str(L1%1000)
		#Timestamp = time.strftime(infile[:2] + ":" + "%M:%S", time.gmtime(L1/1000)) + '.' + str(L1%1000)
		Timestamp = long(L1) + dateWithoutMilisec
		Ask = "%.3f" % (L2/1000)
		Bid = "%.3f" % (L3/1000)
		AskVolume = "%.2f" % (L4*1000000)
		BidVolume = "%.2f" % (L5*1000000)
		#TODO: check if long needed
		ts.append(long(Timestamp))
		ask.append(float(Ask))
		bid.append(float(Bid))
		askV.append(float(AskVolume))
		bidV.append(float(BidVolume))
#		df = df.append(DataFrame(randn(6, 4))
		#line = Timestamp, Ask, Bid, AskVolume, BidVolume
		#TicksData.append((line))
		index += chunksize
	f.close()
	d = {'ask' : ask, 'bid' : bid, 'askV' : askV, 'bidV' : bidV}
	return DataFrame(d, index=ts)

def handleBi5(infile, fileDataFrame):

    if os.path.getsize(infile) == 0:
        return fileDataFrame

    array = infile.split('/')
    print array
    alen = len(array)

    dateWithoutHour = long(datetime(int(array[alen-4]),int(array[alen-3]),int(array[alen -2])).strftime("%s"))
    dateWithoutMilisec = (dateWithoutHour+int(array[alen-1].split('_')[0].split('h')[0])*3600)*1000
    subprocess.call("xz -dkc --suffix=bi5 " + infile + ">tmp.bin", shell=True)


    hdfDir = "./hdf/" + infile.split('/')[2]
    if not os.path.exists(hdfDir):
        os.makedirs(hdfDir)
    cvsFileName = hdfDir + "/" + infile.split('/')[3]

    if fileDataFrame.empty:
        if os.path.exists(cvsFileName):
            fileDataFrame =	read_csv(cvsFileName, index_col=0)
        else:
            fileDataFrame = DataFrame()

    fileDataFrame = fileDataFrame.append(processBinFile("tmp.bin", dateWithoutMilisec))

    print fileDataFrame.iloc[0]
    return fileDataFrame

#	print dir(fileDataFrame)
#	print help(fileDataFrame.append)

#dataFrame = DataFrame()
#
#for line in fileinput.input():
#    print "kk " + line
#    dataFrame = handleBi5(line.rstrip(),dataFrame)
#
#dataFrame.to_csv('test.csv')	

class ForexBi5DataFeeder( DataFeeder ):
    
    def __init__(self, startDate, endDate, currency):
        super(ForexBi5DataFeeder,self).__init__(startDate, endDate)
        self.currency = currency
        self.dfPosition = 0
        self.yearsIndex = 0
        self.monthIndex = 0
        self.daysIndex = 0
        self.hoursIndex = 0
        self.loadFirstDataFrame()
        print self.df.shape
        
                                        
    def loadFirstDataFrame(self):
        self.yearsList = os.listdir('bi5/' + self.currency + '/')
        self.yearsList.sort()
        for a in range(len(self.yearsList)):
            if int(self.yearsList[a]) == self.startDate.year:
                self.yearsIndex = a
                self.year = self.yearsList[a]
                self.monthList = os.listdir('bi5/' + self.currency + '/' + self.year +'/')
                self.monthList.sort()
                for b in range(len(self.monthList)):
                    if int(self.monthList[b]) == self.startDate.month:
                        self.monthIndex = b
                        self.month = self.monthList[b]
                        self.dayList = os.listdir('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/')
                        self.dayList.sort()
                        for c in range(len(self.dayList)):
                            if int(self.dayList[c]) == self.startDate.day:
                                self.dayIndex = c
                                self.day = self.dayList[c]
                                self.hourList = os.listdir('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/' + self.day + '/')        
                                self.hourList.sort()
                                for d in range(len(self.hourList)):
                                    self.hour = self.hourList[d]
                                    if (os.stat('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/' + self.day + '/' + self.hour).st_size > 0):
                                        self.hourIndex = d                                        
                                        self.df = self.handleBi5('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/' + self.day + '/' + self.hour)
                                        self.dfPosition = -1
                                        return
                                        
    def checkEndDate(self):
        self.debugKK(1, 'checking end date ' + self.year + ' ' + self.month + ' ' + self.day)
        curDate = date(int(self.year), int(self.month), int(self.day))
        if curDate >= self.endDate:
            return True
        return False
        
    def debugKK(self, level, txt):
        if (level > 0):
            print txt
        
    def newYear(self):
        if (self.yearsIndex + 1) == len(self.yearsList):
            return None
        else:
            self.yearsIndex += 1
            self.year = self.yearsList[self.yearsIndex]
            self.monthList = os.listdir('bi5/' + self.currency + '/' + self.year +'/')
            self.monthList.sort()
            self.monthIndex = -1
            return self.newMonth()
                            
        
    def newMonth(self):
        self.debugKK(2,self.monthList)
        self.debugKK(2,'month poz ' + str(self.monthIndex + 1) + ' size ' + str(len(self.monthList)));
        if (self.monthIndex + 1) == len(self.monthList):
            return self.newYear()
        else:
            self.monthIndex += 1
            self.month = self.monthList[self.monthIndex]
            self.dayList = os.listdir('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/')
            self.dayList.sort()
            self.dayIndex = -1                                                                                           
            return self.newDay()
                                     
    def newDay(self):
        self.debugKK(1,self.dayList)
        self.debugKK(1,'day poz ' + str(self.dayIndex + 1) + ' size ' + str(len(self.dayList)));
        if (self.dayIndex + 1) == len(self.dayList):
            return self.newMonth()
        else:
            self.dayIndex += 1
            self.day = self.dayList[self.dayIndex]
            if self.checkEndDate():
                return None
            self.hourList = os.listdir('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/' + self.day + '/')        
            self.hourList.sort()
            self.hourIndex = -1                                                                                        
            return self.newHour()
                                     
    def newHour(self):
        self.debugKK(0,'hour poz ' + str(self.hourIndex + 1) + ' size ' + str(len(self.hourList)));
        self.debugKK(0,self.hourList)
        if (self.hourIndex + 1) == len(self.hourList):
            return self.newDay()
        else:
            self.hourIndex += 1                                        
            self.hour = self.hourList[self.hourIndex]
            self.debugKK(0,'new hour ' + self.hour)
            if (os.stat('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/' + self.day + '/' + self.hour).st_size > 0):
                self.df = self.handleBi5('bi5/' + self.currency + '/' + self.year + '/' + self.month + '/' + self.day + '/' + self.hour)
                self.debugKK(0,'new df size ' + str(self.df.shape[0]))
                self.dfPosition = -1
                return self.getData()
            else:
                return self.newHour()
                                        
    def getData(self):
        self.debugKK(0,'df poz ' + str(self.dfPosition + 1) + ' size ' + str(self.df.shape[0]))
        if (self.dfPosition + 1) == self.df.shape[0]:
            return self.newHour()
        else:
            self.dfPosition += 1
            return self.df.iloc[self.dfPosition]
                    
        
                                
                
    
    def handleBi5(self, infile):
        if os.path.getsize(infile) == 0:
            return None
    
        array = infile.split('/')
        #print array
        alen = len(array)
    
        dateWithoutHour = long(datetime(int(array[alen-4]),int(array[alen-3]),int(array[alen -2])).strftime("%s"))
        dateWithoutMilisec = (dateWithoutHour+int(array[alen-1].split('_')[0].split('h')[0])*3600)*1000
        subprocess.call("xz -dkc --suffix=bi5 " + infile + ">tmp.bin", shell=True)
    
        return processBinFile("tmp.bin", dateWithoutMilisec)
    
    
#    def getData(self):
#        yearsList = os.listdir('bi5/EURUSD/')
#        yearsList.sort()
#        print self.startDate.year
#        for year in yearsList:
#            if year >= self.startDate.year:
#                monthList = os.listdir('bi5/EURUSD/')
          
          
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

        
        
          
                
feeder = ForexBi5DataFeeder(date(2012, 1, 1),date(2012, 1, 2), 'EURUSD')

#broker = Broker()
#wallet = Wallet(25000, BuyForOneTenthOfWalletBuyStrategy(), SellIfUpBy10OrDownBy5SellStrategy(), broker)
alg = RolingMeanAlgorithm(5,20)

#sim = Simulator(date(2012, 1, 1), date(2012, 1, 2), wallet, alg, feeder)



dataFrame = DataFrame()
signals = Series()

curFeed = feeder.getData()
while curFeed is not None:
    dataFrame = dataFrame.append([curFeed])
    #print curFeed
    signal = alg.getBuySignals(curFeed)
    signals = signals.append(Series(signal[0], index = [signal[1]]))    
    curFeed = feeder.getData()

dataFrame['ask'].plot();
#rolling_mean(dataFrame['ask'], 20).plot()
#rolling_mean(dataFrame['ask'], 5).plot()
#print rolling_mean(dataFrame['ask'], 20)[20:30]
#print rolling_mean(dataFrame['ask'], 5)[20:30]
#print signals[20:30]
signals.plot()
plt.show()

