from django.conf.urls import patterns, url

from JhaneGlove import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^callibration$', views.callibration, name='callibration'), 
    url(r'^test/$', views.test , name='test'), 
    url(r'^testData/$', views.testData , name='testData'), 
    url(r'^train/$', views.trainTheNetwork , name='train'), 
    url(r'^train_page/$', views.goToTrainPage , name='train_page'), 
    url(r'^add/$', views.addData , name='addData'), 
    url(r'^rec/$', views.recognize , name='recognize'),
    url(r'^do_recognize/$', views.ajaxRecognize , name='ajaxRecognize'),
    
)