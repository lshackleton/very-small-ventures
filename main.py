#!/usr/bin/env python
"""
aptauction

We use the webapp.py WSGI framework to handle CGI requests, using the
wsgiref module to wrap the webapp.py WSGI application in a CGI-compatible
container. See webapp.py for documentation on RequestHandlers and the URL
mapping at the bottom of this module.

We use Django templates, which are described at
http://www.djangoproject.com/documentation/templates/. We define a custom
Django template filter library in templatefilters.py for use in dilbertindex
templates.
"""

__author__ = '(Bill Ferrell)'

import cgi
import datetime
import htmlentitydefs
import math
import os
import re
import sgmllib
import sys
import time
import urllib
import logging
import wsgiref.handlers
import traceback
import random

from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import datastore_errors
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import search
from google.appengine.ext import bulkload
from google.appengine.ext import db

## Set logging level.
logging.getLogger().setLevel(logging.INFO)

# Add our custom Django template filters to the built in filters
template.register_template_library('templatefilters')

# Set to true to see stack traces and template debugging information
_DEBUG = True


class BaseRequestHandler(webapp.RequestHandler):
  """The common class for all verysmallventures requests"""

  def handle_exception(self, exception, debug_mode):
    exception_name = sys.exc_info()[0].__name__
    exception_details = str(sys.exc_info()[1])
    exception_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
    logging.error(exception_traceback)
    exception_expiration = 600 # seconds 
    mail_admin = "wferrell@gmail.com" # must be an admin -- be sure to remove before committing
    sitename = "verysmallventures"
    throttle_name = 'exception-'+exception_name
    throttle = memcache.get(throttle_name)
    if throttle is None:
        memcache.add(throttle_name, 1, exception_expiration)
        subject = '[%s] exception [%s: %s]' % (sitename, exception_name,
                                               exception_details)
        mail.send_mail_to_admins(sender=mail_admin,
                                 subject=subject,
                                 body=exception_traceback)

    values = {}
    template_name = 'error.html'
    #if users.is_current_user_admin():
    #    values['traceback'] = exception_traceback
    values['traceback'] = exception_traceback
    directory = os.path.dirname(os.environ['PATH_TRANSLATED'])
    path = os.path.join(directory, os.path.join('templates', template_name))
    self.response.out.write(template.render(path, values, debug=_DEBUG))

  def generate(self, template_name, template_values={}):
    """Generates the given template values into the given template.

    Args:
        template_name: the name of the template file (e.g., 'index.html')
        template_values: a dictionary of values to expand into the template
    """

    # Populate the values common to all templates
    values = {
      #'user': users.GetCurrentUser(),
      'debug': self.request.get('deb'),
      'user': users.GetCurrentUser(),
      'login_url': users.CreateLoginURL(self.request.uri),
      'logout_url': users.CreateLogoutURL(self.request.uri),

    }
    values.update(template_values)
    directory = os.path.dirname(os.environ['PATH_TRANSLATED'])
    path = os.path.join(directory, os.path.join('templates', template_name))
    self.response.out.write(template.render(path, values, debug=_DEBUG))


class HomePageHandler(BaseRequestHandler):
  """  Generates the start/home page.
  """

  def get(self, garbageinput=None):
    logging.info('Visiting the homepage')

    self.generate('home.html', {
    })

class AboutPageHandler(BaseRequestHandler):
  """  Generates the about page.
  """

  def get(self, garbageinput=None):
    logging.info('Visiting the aboutpage')

    self.generate('about.html', {
    })

class VenturesPageHandler(BaseRequestHandler):
  """  Generates the ventures page.
  """

  def get(self, garbageinput=None):
    logging.info('Visiting the venturespage')

    self.generate('ventures.html', {
    })

class ContactPageHandler(BaseRequestHandler):
  """  Generates the contact page.
  """

  def get(self, garbageinput=None):
    logging.info('Visiting the contactpage')

    self.generate('contact.html', {
    })

# Map URLs to our RequestHandler classes above
_VERYSMALLVENTURES_URLS = [
# after each URL map we list the html template that is displayed
   ('/', HomePageHandler), #home.html
   ('/index', HomePageHandler), #home.html
   ('/index.html', HomePageHandler), #home.html
   ('/home', HomePageHandler), #home.html
   ('/about', AboutPageHandler), #about.html
   ('/ventures', VenturesPageHandler), #ventures.html
   ('/contact', ContactPageHandler), #contact.html
   ('/.*$', HomePageHandler), #home.html
]


def main():
  application = webapp.WSGIApplication(_VERYSMALLVENTURES_URLS, debug=_DEBUG)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
