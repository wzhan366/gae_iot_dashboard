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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#datastore
class Lamp(ndb.Model):
  id_ = ndb.IntegerProperty(default=0)
  switch = ndb.IntegerProperty(default=0)
  info = ndb.TextProperty(default="You should discribe this device a little bit!")

class Controller(ndb.Model):
  user_email = ndb.StringProperty(default="me@email.com")
  verified = ndb.BooleanProperty(default=False)

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


class HomePage(_BaseHandler):
    def get(self):
        logging.info('HomePage class requested')

        query = Lamp.query()
        query = query.order(
                  -Lamp.id_)
        results = query.fetch(5)
        # print 'query results', results
        self.template_values['home_stats'] = results

        template = jinja_environment.get_template('home.template')
        self.response.out.write(template.render(self.template_values))

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
        # print 'buttons', self.request.get('update'), self.request.get('delete')
        if access:
            if access.verified:
                # get the device if it is in database
                if self.request.get('update'):
                    # print 'botton', self.request.get('update')
                    if self.request.get('id') != '':
                        lamp_key = ndb.Key('Lamp', self.request.get('id'))
                        if self.request.get('update') == '1':
                            lamp = lamp_key.get()
                            print 'IN'
                            if lamp:
                                lamp.id_ = int(self.request.get('id'))
                                lamp.switch = int(self.request.get('switch'))
                                print 'the get info', self.request.get('info')
                                if str(self.request.get('info')):
                                    lamp.info= str(self.request.get('info'))
                                lamp.put()
                            else:
                                lamp = Lamp(key=ndb.Key("Lamp",self.request.get('id')))
                                lamp.id_ = int(self.request.get('id'))
                                lamp.switch = int(self.request.get('switch'))
                                print '!!!!!!!!!!!!the get info', self.request.get('info')
                                if str(self.request.get('info')):
                                    lamp.info=str(self.request.get('info'))
                                lamp.put()
                            message = 'appengine,' + self.request.get('id') + ',' + self.request.get('switch')
                            sqs_write(message)
                        else:
                            # print 'innnnnnnnnnnnnn delete'
                            lamp_k = ndb.Key('Lamp', self.request.get('id'))
                            # print 'in lammmmmmmmmmmmmp' ,lamp
                            if lamp_k:
                                lamp_k.delete()
                                message = 'appengine,' + self.request.get('id') + ',' + '0'
                                sqs_write(message)
                    self.redirect('/control')
                #table form
                # print 'table botton', self.request.get('t_botton')
                #this part works correct
                if self.request.get('t_botton'):
                    if self.request.get('t_botton')  == '1': #table update
                        lamp_key = ndb.Key('Lamp', self.request.get('device_id'))
                        print 'table delete ', lamp_key
                        lamp = lamp_key.get()
                        print 'LAAAAAAAAAAAAAAAA', lamp
                        lamp.switch = int(self.request.get('device_switch'))
                        lamp.put()
                        message = 'appengine,' + self.request.get('device_id') + ',' + self.request.get('device_switch')
                    else:
                        lamp_key = ndb.Key('Lamp', self.request.get('device_id'))
                        lamp_key.delete()
                        message = 'appengine,' + self.request.get('device_id') + ',' + '0'

                    sqs_write(message)
                    self.redirect('/control')
                    #correct
            else:
                self.template_values['denied'] = 'True'
                template = jinja_environment.get_template('control.template')
                self.response.out.write(template.render(self.template_values))
        else:
            self.template_values['denied'] = 'True'
            template = jinja_environment.get_template('control.template')
            self.response.out.write(template.render(self.template_values))


from bigquery import query_bigquery
class BigqueryPage(_BaseHandler):
    def get(self):
        logging.info('NewControlCommand class requested')
        sql = 'SELECT \
                mac, \
                year(timeStamp),\
                month(timeStamp),\
                day(timeStamp),\
                hour(timeStamp),\
                minute(timeStamp),\
                second(timeStamp), \
                temp,\
                FROM\
                  [spry-truck-132223:streaming_1.monitor_1]\
                where day(timeStamp) = 17 and mac = '
        # sql += "'" + '0013a20040e44261' + "'" + ' order by temp DESC'
        query = query_bigquery(sql)
        results = []
        for row in query:
            r = [field['v'] for field in row['f']]
            # 2016-09-18 20:24:27
            time = str(r[1]) + '-' + str(r[2]) + '-' + str(r[3]) + ' ' + str(r[4]) + ':' + str(r[5]) + ':' + str(r[6])
            results.append([r[0], time, r[-1]])
        self.template_values['bigquery'] = results
        template = jinja_environment.get_template('bigquery.template')
        self.response.out.write(template.render(self.template_values))

    def post(self):
        logging.info('NewControlCommand class requested')

        d_name = self.request.get('device_name')
        d_mac = self.request.get('device_mac')
        date_b = self.request.get('beginDate')
        date_e = self.request.get('endDate')
        sort_by = self.request.get('sort')

        sql = 'select mac, timeStamp, temp from [spry-truck-132223:streaming_1.monitor_1] where day(timeStamp) = 17 and '

        # if d_name:
        #     sql += ''
        if d_mac:
            sql += ' mac = ' + "'" + d_mac + "'"

        if sort_by:
            sql += ' order by timeStamp'
        print '00000000000000our sql is ', sql
        query = query_bigquery(sql)
        results = []
        for row in query:
            results.append([field['v'] for field in row['f']])
        self.template_values['home_stats'] = results
        template = jinja_environment.get_template('bigquery.template')
        self.response.out.write(template.render(self.template_values))

class Admin(_BaseHandler):
    def get(self):
        logging.info('Admin class requested')
        query = Controller.query()
        query = query.order(
                  -Controller.verified)
        results = query.fetch()
        # print 'query results', results
        self.template_values['controller'] = results
        template = jinja_environment.get_template('admin.template')
        self.response.out.write(template.render(self.template_values))

    def post(self):
        logging.info('Admin class requested')
        if self.request.get('user_email').lower():
            if self.request.get('h_button') == '1': # which is a update

                access_key = ndb.Key('Controller', self.request.get('user_email').lower())
                access = access_key.get()
                # print 'access', access, 'user_email', self.request.get('user_email')
                if access:
                    if self.request.get('verified') == 'y':
                        access.verified= True
                    else:
                        access.verified= False
                    access.put()
                else:
                    #Device doesn't yet exist, create a new device with input values
                    control = Controller(key=ndb.Key("Controller",self.request.get('user_email').lower()))
                    control.user_email=self.request.get('user_email').lower()
                    if self.request.get('verified') == 'y':
                        control.verified= True
                    else:
                        control.verified= False
                    control.put()
            else: #which means delete the user
                access_key = ndb.Key('Controller', self.request.get('user_email').lower())
                if access_key:
                    access_key.delete()
        self.redirect('/admin')

app = webapp2.WSGIApplication([
    # ('/bigquery', BigqueryPage),
  ('/control', NewControlCommand),
  ('/admin', Admin),
  ('/', HomePage)],
  debug=True)
