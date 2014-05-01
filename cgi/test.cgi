#!/usr/bin/python

import os
import Cookie
import datetime
import random

expiration = datetime.datetime.now() + datetime.timedelta(days=30)
cookie = Cookie.SimpleCookie()
cookie["session"] = random.randint(0, 1000000000)
cookie["session"]["domain"] = ".jayconrod.com"
cookie["session"]["path"] = "/"
cookie["session"]["expires"] = \
  expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")

print "Content-type: text/plain"
print cookie.output()
print
print "Cookie set with: " + cookie.output()