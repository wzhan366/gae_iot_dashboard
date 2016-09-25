#!/usr/bin/env python

import os
import datetime
import webapp2
import logging

class TasksPage(webapp2.RequestHandler):
  def get(self):
    logging.info('TasksPage class requested')
    self.response.out.write('TasksPage class requested')

app = webapp2.WSGIApplication([
  ('/tasks', TasksPage)],
  debug=True)
