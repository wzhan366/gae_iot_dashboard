#!/usr/bin/env python

import jinja2
import os
import datetime
import webapp2
import logging
import json

from google.appengine.api import users
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from google.appengine.ext import ndb
from sqs import sqs_write


from control_page import NewControlCommand
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class _BaseHandler(webapp2.RequestHandler):
  def initialize(self, request, response):
    super(_BaseHandler, self).initialize(request, response)

    self.user = users.get_current_user()

    if self.user:
      self.template_values = {
          'user': self.user,
          'is_admin': users.is_current_user_admin(),
          'logout_url': users.create_logout_url('/'),
          'versionid' : os.environ['CURRENT_VERSION_ID']}
    else:
      self.template_values = {'login_url': users.create_login_url(self.request.url)}

class NewControlCommand(_BaseHandler):
    def get(self):
        logging.info('NewControlCommand class requested')
        query = Lamp.query()
        query = query.order(
                  -Lamp.id_)
        results = query.fetch()
        # print 'query results', results

        self.template_values['events'] = results

        template = jinja_environment.get_template('control.template')
        self.response.out.write(template.render(self.template_values))

    def post(self):
        logging.info('NewControlCommand class requested')
        #Look for existing device based on id
        control_key = ndb.Key('Controller', self.user.email())
        access = control_key.get()
        print self.user.email()
        print 'buttons', self.request.get('update'), self.request.get('delete')
        if access:
            if access.verified:
                # get the device if it is in database
                lamp_key = ndb.Key('Lamp', int(self.request.get('id')))
                lamp = lamp_key.get()

                if not lamp:
                    #Device doesn't yet exist, create a new device with input values
                    lamp = Lamp(key=ndb.Key("Lamp",int(self.request.get('id'))))
                    lamp.id_=int(self.request.get('id'))
                    lamp.switch=int(self.request.get('switch'))
                    lamp.info=str(self.request.get('info'))
                    lamp.put()
                else:
                    lamp.switch = int(self.request.get('switch'))
                    if str(self.request.get('info')):
                        lamp.info=str(self.request.get('info'))
                    lamp.put()
                message = 'appengine,' + self.request.get('id') + ',' + self.request.get('switch')
                sqs_write(message)
                self.redirect('/control')
            else:
                self.template_values['denied'] = 'True'
                template = jinja_environment.get_template('control.template')
                self.response.out.write(template.render(self.template_values))
        else:
            self.template_values['denied'] = 'True'
            template = jinja_environment.get_template('control.template')
            self.response.out.write(template.render(self.template_values))
