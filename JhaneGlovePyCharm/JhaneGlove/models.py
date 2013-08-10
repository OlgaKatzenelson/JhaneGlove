from django.db import models
import datetime
import os
import pickle
import cPickle
import time
import pybrain

from pybrain.datasets import *
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import *

from django.utils import timezone
from django import template
from django.core import serializers


register = template.Library()

class UserData(models.Model):
    userId = models.IntegerField(0)
    startCallibrationTime = models.BigIntegerField(0)
    stopCallibrationTime = models.BigIntegerField(0)
    minValuesList = models.TextField(null=True)
    maxValuesList = models.TextField(null=True)
    isDirt = models.IntegerField(0)

    def __unicode__(self):
        return str(self.userId) + "( " + str(self.startCallibrationTime) + " : " + str(self.stopCallibrationTime) + " )"

class SerialRawData(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.IntegerField(0)
    time = models.BigIntegerField(0)
    data = models.CharField(max_length=255)


    def __unicode__(self):
        return str(self.userId) + "( " + str(self.time) + " : " + str(self.data) + " )"


class NN(models.Model):
    TEST_MESSAGE = '{0} will be {1}'
    INPUT_SIZE = 6
    userId = models.IntegerField(0)
    ds = models.BinaryField()
    net =  models.BinaryField();
    pickled_net = models.TextField()
    totalError = models.FloatField(100, null=True);
    userName = models.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(NN, self).__init__(*args, **kwargs)
        self.ds = ClassificationDataSet(self.INPUT_SIZE, 1, nb_classes=5)
        self.net = FeedForwardNetwork()
        #         self.ds = ClassificationDataSet(6, 1, nb_classes=4)
        #         self.net = FeedForwardNetwork()
        self.net.addInputModule(LinearLayer(self.INPUT_SIZE, name='in'))
        self.net.addModule(SigmoidLayer(26, name='hidden_0')) #40 24
#        self.net.addModule(SigmoidLayer(6, name='hidden_1')) #SigmoidLayer
        self.net.addOutputModule(LinearLayer(1, name='out'))
        self.net.addConnection(FullConnection(self.net['in'], self.net['hidden_0']))
#        self.net.addConnection(FullConnection(self.net['hidden_0'], self.net['hidden_1']))
#        self.net.addConnection(FullConnection(self.net['hidden_1'], self.net['out']))
        self.net.addConnection(FullConnection(self.net['hidden_0'], self.net['out']))
        self.net.sortModules()
        self.trainer = BackpropTrainer(self.net, dataset=self.ds, momentum=0.1, verbose=False, weightdecay=0.01, learningrate=0.003)  # , learningrate=0.01, verbose=True, learningrate=0.1, momentum=0.9

    def loadDataForTrain(self):
        cells = Cell.objects.filter(nn_id = self.id, forTest = False)
        if(len(cells)>0):
            self.ds.clear()
            for cell in cells:
                data = self.convertToIntArray(cell.data.split())
                print 'try to add {0} : {1}'.format(data, cell.dataClass)
                self.ds.addSample(data , (cell.dataClass))

    def convertToIntArray(self, origArray):
        newArray = []
        for val in origArray:
            newArray.append(int(val))
        return newArray

    def train(self):
        self.loadDataForTrain()
        trained = False
        acceptableError = 0.001
        counter = 20
        o = 0
        # train until acceptable error reached
        while trained == False and counter > 0:
            self.trainer.trainOnDataset(self.ds, 200)
            error = self.trainer.train()
            if error < acceptableError :
                trained = True
#            if(counter < 15 and o ==0):
#                self.trainer.momentum=0.1
            if(counter < 10 and o ==0):
                self.trainer.momentum=0.2
            if(counter < 5 and o ==0):
                self.trainer.momentum=0.5
                counter = 15
                o = 1
            counter -= 1
            print error
            print 'counter = {0}'.format(counter)
        self.totalError = error
        print "Train Finished"
        userMessage = "Training was successful.   "
        if (counter <= 0):
            userMessage = "Training failed.   "

        self.pickled_net = cPickle.dumps(self.net)

        self.test()
        return userMessage


    def train1(self):
#        self.net.reset()
        self.loadDataForTrain()
        trained = False
        acceptableError = 0.003 #0.001
        counter = 15
        o = 0
        # train until acceptable error reached
        while trained == False and counter > 0:
#            self.trainer.trainUntilConvergence()
            self.trainer.trainOnDataset(self.ds, 100)
#            self.trainer.trainEpochs(200)
#            self.trainer.testOnClassData(dataset = self.ds)

            error = self.trainer.train()
            self.pickled_net = cPickle.dumps(self.net)
            if error < acceptableError:
#                if self.test() >80:
                trained = True
#            if(counter < 10 and o ==0):
#                self.trainer.momentum=0.2
            if(counter < 5 and o ==0):
                self.trainer.momentum=0.6
                counter = 10
                o = 1

            counter -= 1
            print error
            print 'counter = {0}'.format(counter)
        self.totalError = error
        self.pickled_net = cPickle.dumps(self.net)
        print "Train Finished"
        userMessage = "Training was successful.   "
        if (self.test() <= 80):
            userMessage = "Training failed.   "
#            print "-------------------------------------"
#            self.train1()


        self.test()
        return userMessage

    def test(self):
        totalSuccess = 0;

        self.net= cPickle.loads(str(self.pickled_net))
        cells = Cell.objects.filter(nn_id = self.id, forTest = True)
        totalCounter = len(cells);
        if(totalCounter>0):
            for cell in cells:
                data = self.convertToIntArray(cell.data.split())
#                print 'test {0} : {1}'.format(data, cell.dataClass)
                totalSuccess+=self.activateAndTest(data , cell.dataClass)

        print "total {0}  success {1}".format(totalCounter, totalSuccess);
        if(totalCounter == totalSuccess):
            return 0;
        return   float(totalSuccess) / totalCounter * 100

    def activate(self, data):
        return self.net.activate(data)

    def activateOnSet(self, dataSet):
        result = ''
        for data in dataSet:
            result = self.net.activate(data)

        return result

    def activateAndTest(self, data, dataClass):
        activationResult = self.net.activate(data);
        print self.TEST_MESSAGE.format(activationResult, dataClass)
        if(self.numbersClose(activationResult,dataClass)==False):
            return 0;
        return 1;

    def numbersClose(self, n1, n2):
        if type(n1) == type(int()):
            if(abs(n1-n2) < 0.2):
                return True
        if(abs(n1[0]-n2) < 0.2):
            return True
        return False

class Cell(models.Model):
    nn = models.ForeignKey(NN)
    data = models.CharField(max_length=200)
    dataClass = models.IntegerField(0)
    userId = models.IntegerField(0)
    forTest = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.data) + " : " + str(self.dataClass)

class DataReader(models.Model):
    TIME_WINDOW = 5

    def loadData(self, userId):
        currentTime = int(time.time())

        rawData = SerialRawData.objects.filter(userId = userId, time__range=(str(currentTime - self.TIME_WINDOW), currentTime))
        #clear old data
        self.removeData(userId, currentTime)

        return rawData

    def loadSingleData(self, _userId, timestamp):
        rawData = SerialRawData.objects.filter(userId = _userId, time__range=(timestamp, str(timestamp + self.TIME_WINDOW)))
        if(len(rawData) > 0):
            return rawData[0].data

        return ""


    def loadDataInRange(self, _userId, startTime, stopTime):
        return SerialRawData.objects.filter(userId = _userId, time__range=(startTime, stopTime))


    def removeData(self, userId, timestamp):
        SerialRawData.objects.filter(userId = userId, time__lte=timestamp).delete()


    @register.filter()
    def contains(self, value, arg):
        return arg in value