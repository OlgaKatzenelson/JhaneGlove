from django.conf.urls import patterns, url

from JhaneGlove import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^callibration$', views.callibration, name='callibration'),
    url(r'^startCalibration', views.startCallibration, name='startCallibration'),
    url(r'^stopCalibration', views.stopCallibration, name='stopCallibration'),
    url(r'^test/$', views.test , name='test'),
    url(r'^testData/$', views.testData , name='testData'), 
    url(r'^train/$', views.trainTheNetwork , name='train'),
    url(r'^train_page/$', views.goToTrainPage , name='train_page'), 
    url(r'^add/$', views.addData , name='addData'),
    url(r'^doRecognize/$', views.ajaxRecognize , name='ajaxRecognize'),
    url(r'^recognition/$', views.recognize , name='recognize'),
    url(r'^doClearOldTrainingData/$', views.clearOldTrainingData , name='clearOldTrainingData'),


    
)