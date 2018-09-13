import os
from logging import getLogger
from datetime import timedelta

APPLICATION_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # app package name

BASE_URL = 'http://54.149.37.75:5001'

DEBUG = False
TESTING = False

#SQLALCHEMY_DATABASE_URI = 'mysql://root:R00t@123@69.64.41.105/octad'
SQLALCHEMY_DATABASE_URI = 'mysql://root:octad#123@127.0.0.1/octad'
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_POOL_RECYCLE = 60 * 60
SQLALCHEMY_POOL_TIMEOUT = 20
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

LOGGERS = [getLogger('sqlalchemy')]  # TODO check the getlogger of sqlalchemy

# set a 'SECRET_KEY' to enable the Flask session cookies
SECRET_KEY = 'x$ow].em(2mI$,c0ghj'

BLUEPRINTS = ['views.base.baseRoute', 'views.dashboard.dashboardRoute', 'views.profile.profile',
			  'views.custom_api.apiRoute']

RSCRIPT_PATH = '/home/ec2-user/R-3.4.3/bin/Rscript'
RREPO_PATH = '/var/www/html/OCTAD_PORTAL-master/'
RREPO_OUTPUT = APPLICATION_ROOT + '/static/data/'

WTF_CSRF_ENABLED = False
REMEMBER_COOKIE_DURATION = timedelta(days=1)

