from django.shortcuts import render

from django.http import  HttpResponse
#from django.conf import settings
from django.contrib.sessions.models import Session

from JhaneGlove.models import Cell, NN, DataReader, UserData, SerialRawData
from JhaneGlovePyCharm import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import json
import time

jsonDec = json.decoder.JSONDecoder()
nn = NN( id = 1)
dataReader = DataReader()

#@login_required
def index(request):
    return render(request, 'JhaneGlove/index.html')

@login_required
def callibration(request):
    return render(request, 'JhaneGlove/callibration.html')

@login_required
def startCallibration(request):
    try:
        userData = UserData.objects.get( userId = request.user.id)
    except ObjectDoesNotExist:
        userData = UserData( userId = request.user.id)
    userData.startCallibrationTime = str(int(time.time()))
    userData.stopCallibrationTime = -1
    userData.save()
    return getHttpSuccessResponse()

@login_required
def stopCallibration(request):
    try:
        userData = UserData.objects.get( userId = request.user.id)
    except ObjectDoesNotExist:
        userData = UserData( userId = request.user.id)
    userData.stopCallibrationTime = str(int(time.time()))

#    userData.startCallibrationTime = 1374776866
#    userData.stopCallibrationTime = 1374776869
    try:
    #        load calibration data per user
        rawData = SerialRawData.objects.filter(userId = request.user.id, time__range=(userData.startCallibrationTime, userData.stopCallibrationTime))
        for serialRawData in rawData:
            data = serialRawData.data.split("\t")
            if userData.minValuesList != None:  # has prev. info
                minValueList = jsonDec.decode(userData.minValuesList) #convert string to array
                maxValueList = jsonDec.decode(userData.maxValuesList)
                for i in range(len(data)):   #update min and max arrays
                    if int(data[i]) < int(minValueList[i]):
                        minValueList[i] = data[i]
                    if int(data[i]) > int(maxValueList[i]):
                        maxValueList[i] = data[i]

                userData.minValuesList = json.dumps(minValueList) #convert array to string
                userData.maxValuesList = json.dumps(maxValueList)
            else: # first record
                userData.minValuesList = json.dumps(data)
                userData.maxValuesList = json.dumps(data)
    except ObjectDoesNotExist:
        return getHttpResponse(0, "Serial data of the user is empty.   ")

    userData.save()

    return getHttpSuccessResponse()

def test(request):
    return render(request, 'JhaneGlove/test.html')

def recognize(request):
    return render(request, 'JhaneGlove/recognize.html')

def goToTrainPage(request):
    return render(request, 'JhaneGlove/train_page.html')



def addData(request):
    dataClass = request.POST['class_id']
    #   request.session
    forTest  = request.POST['for_test']
    data = dataReader.getDataFromSerial()
    print 'test :: {0}'.format(data)
    if(data != ''):
        cell = Cell(userId = 0)
        cell.data = data
        cell.dataClass = dataClass
        #     try:
        #         nn = NN.objects.get(id = 1)
        #     except ObjectDoesNotExist:
        #         nn = NN(id = 1)
        print '******* forTest = {0}   ***** dataClass = {1}'.format(forTest, dataClass);
        if (forTest == '1'):
            nn.addTestCell(cell)
        else:
            nn.addCell(cell)
        cell.save()
    else:
        print 'empty cell'
        return getHttpResponse(0, "Arduino doesn't connected.   ")

    print "ajax_start id={0}".format(dataClass)
    print nn.cells.__len__()
    return getHttpSuccessResponse()


def testData(request):
#     nn = NN.objects.get(id = 1);
#     print nn.totalError
    rateOfSuccess = nn.test();
    userMessage = '{0}% of success.   '.format(rateOfSuccess);
    return getHttpResponse(1, userMessage)

def trainTheNetwork(request):
#     nn = NN( id = 1);
    nn.addData('');
    userMessage = nn.train();
    nn.save()
    return getHttpResponse(1, userMessage)

def ajaxRecognize(request):
    time.sleep(1)
    data = dataReader.getDataFromSerial()
    result = 'Unknown'
    if data != '':
        result = nn.activate(data.split())[0]
    print "Here"
#    result = data
    print "Recognize result: {0}      data {1}".format(result, data)
#    return getHttpResponse(1, result[0])
    return getHttpResponse(1, result)

def getHttpResponse(status, message):
    to_json = {
        "status": status,
        "message": message
    }
    json_data = json.dumps(to_json)
    return HttpResponse(json_data, mimetype="application/json")

def getHttpSuccessResponse():
    return getHttpResponse(1, '')


