from django.shortcuts import render
import os

from django.http import  HttpResponse
#from django.conf import settings
from django.contrib.sessions.models import Session

from JhaneGlove.models import Cell, NN, SerialReader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import json

READER = SerialReader()
nn = NN( id = 1)
PATH_TO_FILE = os.path.dirname(os.path.dirname(__file__)) + '/serialReader/data.txt'

#@login_required
def index(request):
    print '----------------- ?'

#    f = open( path, 'r' )
    f = file(PATH_TO_FILE, "r")
    try:
        last_line = f.readlines()[-1]
#    for line in f:
#        print( line )
        print last_line
    except:
        print "Empty file"
    f.close()
    print 'end ----------------- ?'

    return render(request, 'JhaneGlove/index.html')

def callibration(request):
    return render(request, 'JhaneGlove/callibration.html')

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
    data = getDataFromSerial()
    if(data != ''):
        cell = Cell(userId = 0)
        cell.data = data
        cell.dataClass = dataClass
        #     try:
        #         nn = NN.objects.get(id = 1)
        #     except ObjectDoesNotExist:
        #         nn = NN(id = 1)
        print '******* forTest = {0}'.format(forTest);
        if (forTest == '1'):
            nn.addTestCell(cell)
        else:
            nn.addCell(cell)
        cell.save()
    else:
        print 'empty cell'
        return getHttpResponse(0, "Arduino doesn't connected.   ")

    print "ajax_start id={0}".format(dataClass)
    print nn.cells
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
    data = getDataFromSerial()
    result = nn.activate(data.split())
    print "Recognize result: {}".format(result)
    return getHttpResponse(1, result[0])

def getDataFromSerial():
    data = ''
    try:
    #         rr  = SerialReader();
    #         print "reader   :{0}".format(rr != None);
        data = READER.readLine()
    #         data = rr.readLine()
    except:
        print 'ReadLine error'
        # data = "2568 540 -17004 -34 -17 -2"
    return data

def getHttpResponse(status, message):
    to_json = {
        "status": status,
        "message": message
    }
    json_data = json.dumps(to_json)
    return HttpResponse(json_data, mimetype="application/json")

def getHttpSuccessResponse():
    return getHttpResponse(1, '')

