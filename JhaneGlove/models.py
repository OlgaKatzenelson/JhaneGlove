from django.db import models
import datetime
import os
import pickle
import pybrain

from pybrain.datasets import *
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import *

from django.utils import timezone
from django import template

register = template.Library()

class Cell(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.CharField(max_length=200)
    dataClass = models.IntegerField(0)
    userId = models.IntegerField(0)

    def __unicode__(self):
        return str(self.data) + " : " + str(self.dataClass)

    def delete(self, *args, **kwargs):
        pass

    def close(self):
        self.ser.close()

class NN(models.Model):
    TEST_MESSAGE = '{0} will be {1}'
    cells = []
    testCells = []
    ds = models.BinaryField()
    net =  models.BinaryField();
    totalError = models.FloatField(100);
    userName = models.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(NN, self).__init__(*args, **kwargs)
        self.ds = ClassificationDataSet(6, 1, nb_classes=5)
        self.net = FeedForwardNetwork()
        #         self.ds = ClassificationDataSet(6, 1, nb_classes=4)
        #         self.net = FeedForwardNetwork()
        self.net.addInputModule(LinearLayer(6, name='in'))
        self.net.addModule(SigmoidLayer(50, name='hidden_0')) #40
        #         self.net.addModule(SigmoidLayer(16, name='hidden_1'))
        self.net.addOutputModule(LinearLayer(1, name='out'))
        self.net.addConnection(FullConnection(self.net['in'], self.net['hidden_0']))
        #         self.net.addConnection(FullConnection(self.net['hidden_0'], self.net['hidden_1']))
        #         self.net.addConnection(FullConnection(self.net['hidden_1'], self.net['out']))
        self.net.addConnection(FullConnection(self.net['hidden_0'], self.net['out']))
        self.net.sortModules()
        self.trainer = BackpropTrainer(self.net, momentum=0.01)  # , learningrate=0.01, verbose=True, learningrate=0.1, momentum=0.9

    def addCell(self, cell):
        self.cells.append(cell)
        print self.cells

    def addTestCell(self, cell):
        self.testCells.append(cell)
        print 'Cell for test added'

    def addData(self, data):
        if(len(self.cells)>0):
            for cell in self.cells:
                data = cell.data.split()
                print 'try to add {0} : {1}'.format(data, cell.dataClass)
                self.ds.addSample(data , (cell.dataClass))
        elif(False == True):
            self.getOldDataSet();
        else:
            self.getNewDataSet()

    def store(self):
        f = open('_learned', 'w')
        pickle.dump(self.net, f)
        f.close()

    def load(self):
        f = open('_learned', 'r')
        self.net = pickle.load(f)
        f.close()

    def train(self):
        trained = False
        acceptableError = 0.001
        counter = 10
        o = 0
        # train until acceptable error reached
        while trained == False and counter > 0:
            self.trainer.trainOnDataset(self.ds, 100)
            error = self.trainer.train()
            if error < acceptableError :
                trained = True
            if(counter < 5 and o ==0):
                self.trainer.momentum=0.5
                counter = 10
                o = 1
            counter -= 1
            print error
            print 'counter = {0}'.format(counter)
        self.totalError = error
        print "Train Finished"
        userMessage = "Training was successful.   "
        if (counter <= 0):
            userMessage = "Training failed.   "
        return userMessage


    def test(self):
        totalCounter = 8;
        totalSuccess = 0;

        if(len(self.testCells)>0):
            totalCounter = len(self.testCells)
            for cell in self.testCells:
                data = cell.data.split()
                totalSuccess+=self.activateAndTest(data , cell.dataClass)
        else:
            totalSuccess+=self.activateAndTest([2580, 480, -16840, -32, -16, -3], 0)
            totalSuccess+=self.activateAndTest([2474, 508, -16708, -31, -10, -4], 0)
            totalSuccess+=self.activateAndTest([2400, -7940, -14868, -36, -18, -2], 1)
            totalSuccess+=self.activateAndTest([2236, -7822, -14720, -94, -17, -13], 1)
            totalSuccess+=self.activateAndTest([1972, 9908, -13348, -198, -17, -8], 2)
            totalSuccess+=self.activateAndTest([2020, 10006, -13080, 11, -20, 2], 2)
            totalSuccess+=self.activateAndTest([-6900, 528, -15932, -88, -75, 23], 3)
            totalSuccess+=self.activateAndTest([-8328, 400, -14460, -40, -52, -5], 3)

        print "total {0}  errors {1}".format(totalCounter, totalSuccess);
        if(totalCounter == totalSuccess):
            return 0;
        return   float(totalSuccess) / totalCounter * 100
    #         print self.TEST_MESSAGE.format(self.net.activate([2580, 480, -16840, -32, -16, -3]), '0')
    #         print self.TEST_MESSAGE.format(self.net.activate([2474, 508, -16708, -31, -10, -4]), '0')
    #         print self.TEST_MESSAGE.format(self.net.activate([2400, -7940, -14868, -36, -18, -2]), '1')
    #         print self.TEST_MESSAGE.format(self.net.activate([2236, -7822, -14720, -94, -17, -13]), '1')
    #         print self.TEST_MESSAGE.format(self.net.activate([1972, 9908, -13348, -198, -17, -8]), '2')
    #         print self.TEST_MESSAGE.format(self.net.activate([2020, 10006, -13080, 11, -20, 2]), '2')
    #         print self.TEST_MESSAGE.format(self.net.activate([-6900, 528, -15932, -88, -75, 23]), '3')
    #         print self.TEST_MESSAGE.format(self.net.activate([-8328, 400, -14460, -40, -52, -5]), '3')

    def activate(self, data):
        return self.net.activate(data)

    def activateAndTest(self, data, dataClass):
        activationResult = self.net.activate(data);
        print self.TEST_MESSAGE.format(activationResult, dataClass)
        if(self.numbersClose(activationResult,0)==False):
            return 1;
        return 0;

    def numbersClose(self, n1, n2):
        if(abs(n1-n2) > 0.2):
            return False
        return True

    def getNewDataSet(self):
        #  data for tests
        self.ds.addSample(('2440', '320', '-17304', '-39', '-18', '-2') , (0))
        self.ds.addSample(('2348', '480', '-17140', '-40', '-17', '-3') , (0))
        self.ds.addSample(('-7080', '-644', '-15564', '-52', '-32', '-11') , (1))
        self.ds.addSample(('-7716', '-992', '-15092', '-56', '-41', '-4') , (1))
        self.ds.addSample(('9776', '484', '-14296', '-42', '0', '3') , (2))
        self.ds.addSample(('9752', '604', '-14232', '-39', '-29', '-5') , (2))
        self.ds.addSample(('2300', '-7240', '-15268', '130', '-30', '-3') , (3))
        self.ds.addSample(('2268', '-7628', '-15280', '-31', '-20', '0') , (3))
        self.ds.addSample(('2140', '-7852', '-15052', '-44', '-16', '6') , (4))
        self.ds.addSample(('2364', '5404', '-16212', '-39', '-18', '-3') , (4))

        #  org data
        self.ds.addSample(("2440    320    -17304    -39    -18    -2".split()) , (0))
        self.ds.addSample(("2348    480    -17140    -40    -17    -3".split()) , (0))
        self.ds.addSample(("-7080    -644    -15564    -52    -32    -11".split()) , (1))
        self.ds.addSample(("-7716    -992    -15092    -56    -41    -4".split()) , (1))
        self.ds.addSample(("9776    484    -14296    -42    0    3".split()) , (2))
        self.ds.addSample(("9752    604    -14232    -39    -29    -5".split()) , (2))
        self.ds.addSample(("2300    -7240    -15268    130    -30    -3".split()) , (3))
        self.ds.addSample(("2268    -7628    -15280    -31    -20    0".split()) , (3))
        self.ds.addSample(("2140    -7852    -15052    -44    -16    6".split()) , (4))
        self.ds.addSample(("2364    5404    -16212    -39    -18    -3".split()) , (4))

    def getOldDataSet(self):
        self.ds.addSample((2568, 540, -17004, -34, -17, -2) , (0))  # pryamo
        self.ds.addSample((2500, 524, -16944, -33, -16, -4) , (0))
        self.ds.addSample((2580, 480, -16840, -32, -16, -3) , (0))
        self.ds.addSample((2520, 576, -16852, -33, -14, -4) , (0))
        self.ds.addSample((2536, 572, -16952, -33, -13, -2) , (0))
        self.ds.addSample((2484, 508, -16708, -31, -11, -4) , (0))
        self.ds.addSample((2584, 372, -16792, -33, -12, -3) , (0))
        self.ds.addSample((2496, 588, -16976, -35, -14, -4) , (0))
        self.ds.addSample((2684, 556, -16916, -35, -12, -8) , (0))
        self.ds.addSample((2624, 484, -16804, -36, -36, -5) , (0))
        self.ds.addSample((2288, 948, -16828, -79, 53, -14) , (0))
        self.ds.addSample((2364, 908, -16788, -35, -17, -4) , (0))
        self.ds.addSample((2464, 940, -16960, -82, 66, -14) , (0))

        self.ds.addSample((2400, -7940, -14868, -36, -18, -2) , (1))  # levo
        self.ds.addSample((2224, -8020, -14660, -42, -17, -3) , (1))
        self.ds.addSample((2284, -7896, -14720, -35, -17, -2) , (1))
        self.ds.addSample((2180, -8092, -14604, -46, -14, -6) , (1))
        self.ds.addSample((2236, -7952, -14820, -94, -17, -13) , (1))

        self.ds.addSample((1972, 9908, -13348, -198, -17, -8) , (2))  # -pravo
        self.ds.addSample((2024, 10316, -13060, -76, -10, -2) , (2))
        self.ds.addSample((2032, 10492, -13304, -33, -19, -6) , (2))
        self.ds.addSample((2020, 10776, -13080, 11, -20, 2) , (2))

        self.ds.addSample((-6900, 528, -15932, -88, -75, 23) , (3))  # -pered
        self.ds.addSample((-8536, 136, -14064, -20, -5, -21) , (3))
        self.ds.addSample((-8328, 364, -14460, -31, -52, -5) , (3))

class DataReader(models.Model):
    PATH_TO_FILE = os.path.dirname(os.path.dirname(__file__)) + '/serialReader/data.txt'
    data = models.CharField(max_length=200)

    def __unicode__(self):
        return self.PATH_TO_FILE

        # The function tried to read data twice. Because of instability of the Arduino
    def getDataFromSerial(self):
        self.data = ''
        data = self.readDataFromSerial()
        if self.data == '':
            self.data = self.readDataFromSerial

        return self.data

    def readDataFromSerial(self):
        data = ''

        f = file(self.PATH_TO_FILE, "r")
        try:
            data = f.readlines()[-1] #last line
            print data
            if self.contains(data , "Arduino") or data.split().__len__() != 6:
                data = ''
        except:
            print "Empty file"
#            data = ''
            # data = "2568 540 -17004 -34 -17 -2"
        f.close()

    @register.filter()
    def contains(self, value, arg):
        return arg in value