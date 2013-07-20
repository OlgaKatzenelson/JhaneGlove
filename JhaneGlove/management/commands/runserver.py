import subprocess
import os
from os import environ

from django.core.management.commands.runserver import BaseRunserverCommand
from django.contrib.sessions.models import Session


from django.conf import settings
import sys

class Command(BaseRunserverCommand):

    def inner_run(self, *args, **options):

        print "yps-------------------"
        s = Session()
        settings.SESSION_KEY = s.session_key
#        path = os.path.join(os.path.dirname(__file__), '../../../serialReader/reader.py')
        path = os.path.dirname(os.path.dirname(__file__)) + '/../../serialReader/reader.py'

#        ROOT_PATH = os.path.join(os.path.dirname(__file__), "../../../")
#
#        sys.path.append(os.path.abspath(ROOT_PATH))
#        MEDIA_ROOT2 = os.path.join(ROOT_PATH, 'templates', 'media')
#
#        print '888888888'
#        print path

#        for dirname, dirnames, filenames in os.walk(os.path.join('media', 'static', 'css')):
#                    print os.path.join(dirpath, filename)


        subprocess.Popen(["python",path])
#        env = environ.copy()
#        subprocess.Popen(["python",path], env={'PATH': MEDIA_ROOT2})
#        subprocess.Popen(["python",path], env = {'PYTHONPATH': '../../static'})

#        settings.TEST = 'ok'

        super(Command, self).inner_run(*args, **options)