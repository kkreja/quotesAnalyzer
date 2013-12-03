# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 18:49:21 2013

@author: kk
"""

#from datetime import date

#!/usr/bin/python
class BuyStrategy( object ):
    """klasa abstrakcyjna tylko definicja interfejsu"""
    def forHowMuchShouldIBuy(self, wallet, currentPrice, direction):
        raise NotImplementedError( "Should have implemented this" )
        
class BuyForOneTenthOfWalletBuyStrategy( BuyStrategy ):
    def forHowMuchShouldIBuy(self, wallet, currentPrice, direction):
        """always return 1/10 of money left from wallet"""
        return wallet.getMoneyLeft()/10
        
class SellStrategy( object ):
    def processOpenPositions(self, wallet, currentPrice):
        raise NotImplementedError( "Should have implemented this" )

class SellIfUpBy10OrDownBy5SellStrategy( SellStrategy ):
    def processOpenPositions(self, wallet, currentPrice):
        positionsToSell = []
        for openPosition in wallet.getOpenPositions:
            if currentPrice > (1.1 * openPosition['buyPrice']) or \
            currentPrice < (0.95 * openPosition['buyPrice']):
                    positionsToSell.append(openPosition)
        return positionsToSell

class Broker( object ):
    """simplest broker always buys always sells"""
    def setCurrentPriceAndTime(self, currentPrice, currentTime):
        self.currentPrice = currentPrice
        self.currentTime = currentTime
    def tryToBuy(self, moneyToInvest,direction):
        return {'buyPrice': self.currentPrice, 
                'nrOfInvested': moneyToInvest/self.currentPrice,
                'time': self.currentTime}
    def tryToSell(self, openPosition):
        lostOrGainedMoney = (self.currentPrice-openPosition['buyPrice'])*openPosition['nrOfInvested']
        openPosition['nrOfInvested'] = 0
        #TODO: zalogowac sprzedaz czy zysk czy strata itp
        return openPosition,lostOrGainedMoney

class Wallet( object ):
    """trzyma informacje o:
        1) kapitale poczatkowym
        2) aktualny stan kapitalu
        3) informacje o posiadanych pozycjach (za ile kupione
                                                po jakiej cenie
                                                i kiedy)"""    
    def __init__(self, initialCapital, buyStrategy, sellStrategy, broker):
        self.initialCapital = self.money = initialCapital
        self.buyStrategy = buyStrategy
        self.sellStrategy = sellStrategy
        self.openPositions = []
        self.broker = broker
        
    def getMoneyLeft(self):
        return self.money        
        
    def useNewBuySignal(self, currentPrice, direction):
        moneyToInvest = self.buyStrategy.forHowMuchShouldIBuy(self, currentPrice, direction)
        if (moneyToInvest > 0):
            newOpenPosition = self.broker.tryToBuy(moneyToInvest,direction)
            if (newOpenPosition != None):
                self.openPositions.append(newOpenPosition)

    def deleteEmptyPositions(self):
        for position in self.openPositions:
            if (position['nrOfInvested'] == 0):
                self.openPositions.remove(position)
        
    def checkIfWeNeedToSellSomething(self, currentPrice):
        positionsToSell = self.sellStrategy.processOpenPositions(self, currentPrice)
        for position in positionsToSell:
            gainedOrLostMoney = self.broker.tryToSell(position)
            self.money += gainedOrLostMoney
        self.deleteEmptyPositions()
        
    def getBroker(self):
        return self.broker

#class FeederSettings( object ):
##    def __init__(self, nrOfMeasurements, timedelta):
#    def __init__(self, nrOfMeasurements):
#        self.nrOfMeasurements = nrOfMeasurements
#        
#    def getNumberOfMeasurements():
#        return self.nrOfMeasurements

class Algorithm( object ):
    """klasa abstrakcyjna tylko definicja interfejsu"""
    
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
        raise NotImplementedError( "Should have implemented this" )
#    
class DataFeeder( object ):
    
    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate
        
    def getData(self):
        raise NotImplementedError( "Should have implemented this" )

#feeder = DataFeeder(date(2012, 1, 1),date(2012, 1, 3))
    
class Simulator( object ):
    """obiekt odpowiedzialny za symulacje. Na wejsciu:
        dataPoczatku
        dataKonca symulacji
        obiekt wallet
        obiekt algorithm
        obiekt datafeeder odpowiedzialny za dostarczanie notowan"""    
#    def __init__(self, beginDate, endDate, wallet, algorithm, feeder):
    def __init__(self, wallet, algorithm, feeder):
#        self.beginDate = beginDate
#        self.endDate = endDate
        self.wallet = wallet
        self.algorithm = algorithm
        self.feeder = feeder
        self.broker = wallet.getBroker()
        
    def run(self):
        feederData = self.feeder.getData()
        while feederData is not None:
            self.currentTime = feederData.name
            self.broker.setCurrentPriceAndTime(feederData['ask'], self.currentTime)
            buySignal = self.algorithm.getBuySignals(feederData)
            if buySignal != 0:
                self.wallet.useNewBuySignal(self, feederData['ask'], buySignal)
            self.wallet.checkIfWeNeedToSellSomething(feederData['bid'])
            feederData = self.feeder.getData()



