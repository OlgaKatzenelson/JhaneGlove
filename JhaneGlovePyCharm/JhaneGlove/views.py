from django.shortcuts import render

from django.http import  HttpResponse
#from django.conf import settings
from django.contrib.sessions.models import Session

from JhaneGlove.models import Cell, NN, DataReader, UserData, ClassData, UsersClassData
from JhaneGlovePyCharm import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.template import Context
import json
import time
import os
from django.db.models import Q
import urllib2
import urllib

jsonDec = json.decoder.JSONDecoder()
dataReader = DataReader()

#@login_required
def index(request):
    _userId = 0;
    userData = None
    if(request.user == None or request.user.id == None):
        userData = UserData.objects.get( userId = 0)
    else:
        _userId = request.user.id
        userData = UserData.objects.get( userId = request.user.id)

    userData.isActive = 1
    userData.save()
    usersData= UserData.objects.filter(~Q(userId = _userId))

    if(len(usersData) > 0):
        for userData in usersData:
            userData.isActive = 0
            userData.save()


    return render(request, 'JhaneGlove/index.html')


def getUserFiles(request):
    if(request.user == None or request.user.id == None):
        return
    path = os.path.dirname(os.path.abspath(__file__))
    userFiles = path + '/../static/images/' + str(request.user.id) + '/set'
    return os.listdir(userFiles)


def getUserClassInfo(request):
    if(request.user == None or request.user.id == None):
        return
    userClasses = UsersClassData.objects.filter(userId=request.user.id)
    userClassInfo = []
    nn = findNNbyUserId(request)
    if(len(userClasses) > 0):
        for userClassData in userClasses:
            classId = userClassData.classId
            symbol = ClassData.objects.get_or_create(classId=userClassData.classId)[0].symbol
            rate = "unknown"
            if(userClassData.rate != None):
                if (nn.numbersClose(int(userClassData.rate) + 1, userClassData.rate) == True or nn.numbersClose(
                    int(userClassData.rate), userClassData.rate) == True):
                    rate = "good"
                else:
                    rate = "bad"

                #            userClassInfo.append({'classId':classId, "symbol":str(symbol), "rate":rate})
            userClassInfo.append([str(classId), str(symbol), rate])
    return userClassInfo


def status(request):
    userClassInfo = getUserClassInfo(request)

    c = Context({"userClassInfo": userClassInfo,
        'filedict' : getUserFiles(request) ,
    })
    return render(request, 'JhaneGlove/status.html', c)

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
    userData.maxValuesList = None
    userData.minValuesList = None
    userData.isDirt = 1;
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
        rawData = DataReader.loadDataInRange(request.user.id, userData.startCallibrationTime, userData.stopCallibrationTime)
        for serialRawData in rawData:
            data = serialRawData.data.replace("\r", "").split("\t")
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
        #clear old data
        DataReader.removeData(request.user.id, userData.stopCallibrationTime)
    except ObjectDoesNotExist:
        return getHttpResponse(0, "Serial data of the user is empty.   ")

    userData.save(force_update=True)

    return getHttpSuccessResponse()

def test(request):
    return render(request, 'JhaneGlove/test.html')

def recognize(request):
    return render(request, 'JhaneGlove/recognize.html')

def goToTrainPage(request):
    userClassInfo = getUserClassInfo(request)

    c = Context({"userClassInfo": userClassInfo,
                 'filedict' : getUserFiles(request) ,
                 })
    return render(request, 'JhaneGlove/train_page.html', c)



def addData(request):
    currentTime =  int(time.time())
    time.sleep(1)
    dataClassValue = request.POST['class_data']

    _userId = 0
    if(request.user != None and request.user.id != None):
        _userId = request.user.id

    # update ClassData and UsersClassData
    dataClassId = ClassData.objects.get_or_create(symbol = dataClassValue)[0].classId
    UsersClassData.objects.get_or_create(userId = _userId, classId = dataClassId)

    #   request.session
    forTest  = request.POST['for_test']
    data = dataReader.loadSingleData(request.user.id, currentTime)
    print 'test :: {0}'.format(data)
    if(data != ''):
        cell = Cell(userId = request.user.id)
        cell.data = data
        cell.dataClass = dataClassId
        nn = findNNbyUserId(request)
        cell.nn = nn

        print '******* forTest = {0}   ***** dataClass = {1}'.format(forTest, dataClassId);
        if (forTest == '1'):
            cell.forTest = True
        cell.save()
    else:
        print 'empty cell'
        return getHttpResponse(0, "Arduino doesn't connected.   ")

    print "ajax_start id={0}".format(dataClassId)
    print len(Cell.objects.filter(nn__userId=request.user.id))
    return getHttpSuccessResponse()

def findNNbyUserId(request):
    _userId = 0
    if(request.user != None and request.user.id != None):
        _userId = request.user.id

    try:
        nn = NN.objects.get(userId=_userId)
    except ObjectDoesNotExist:
        nn = NN(userId=_userId)
        nn.save()
    return nn


def testData(request):
#     print nn.totalError
    nn = findNNbyUserId(request)
    rateOfSuccess = nn.test();
    userMessage = '{0}% of success.   '.format(rateOfSuccess);
    return getHttpResponse(1, userMessage)

def trainTheNetwork(request):
    nn = findNNbyUserId(request)
    userMessage = nn.train1();
    nn.save()
    return getHttpResponse(1, userMessage)

def ajaxRecognize(request):
#    time.sleep(1)
    nn = findNNbyUserId(request)

    userId = 0;
    if(request.user!=None and request.user.id != None):
        userId =  request.user.id;
    data = dataReader.loadData(userId)
    result = 'Unknown'
    if data != '' and len(data) >0:
        tempResult = nn.activateOnSet(data)
        if tempResult != '':
            result = tempResult[0]
            try:
                if (nn.numbersClose(int(result)+1, result) == True):
                   classData =  ClassData.objects.get(classId = int(result)+1)
                   result = classData.symbol
                elif (nn.numbersClose(int(result), result) == True):
                    classData =  ClassData.objects.get(classId = int(result))
                    result = classData.symbol
                else:
                    result = 'Unknown'
            except ObjectDoesNotExist:
                result = 'Unknown'

        print "Recognize result: {0}      data {1}".format(result, data)
    else:
        result = 'Empty'
    return getHttpResponse(1, result)


def clearOldTrainingData(request):
    Cell.objects.filter(nn__userId=request.user.id).delete()
    UsersClassData.objects.filter(userId=request.user.id).delete()
    return getHttpSuccessResponse()

@login_required
def upload(request):
    if request.method == 'POST':
        sign = request.POST['sign']
        if(len(sign) == 0 or len(request.FILES)==0):
            return getHttpResponse(0, "Please select image and enter text of sign.   ")

        file = request.FILES['file']
        userId = request.user.id
        baseDir = 'static/images/'
        destination = ""
        dirname =  str(userId) + "/set/"
        file_name = baseDir + dirname + sign + '.jpg'
        try:
            destination = open(file_name, 'wb+')
        except IOError:
            os.mkdir(os.path.join(baseDir, str(userId)))
            os.mkdir(os.path.join(baseDir+ str(userId), 'set'))
            destination = open(file_name, 'wb+')

        for chunk in file.chunks():
            destination.write(chunk)

    return getHttpSuccessResponse()

def getHttpResponse(status, message):
    to_json = {
        "status": status,
        "message": message
    }
    json_data = json.dumps(to_json)
    return HttpResponse(json_data, mimetype="application/json")

def getHttpSuccessResponse():
    return getHttpResponse(1, '')


