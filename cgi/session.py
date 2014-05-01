#!/usr/bin/python

import cgi, string, sys, os, re, random
import cgitb; cgitb.enable()  # for troubleshooting
import sqlite3
import Cookie
import datetime

from util import *

def create_session(user):
  # Store random string as session number
  # Number of characters in session string
  n=20
  char_set = string.ascii_uppercase + string.digits
  session = ''.join(random.sample(char_set,n)) 

  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()

  # Try to get old session
  t = (user,)
  c.execute('SELECT * FROM sessions WHERE user=?', t)
  row = c.fetchone()
  if row == None:
    # No session for this user. Create one
    s=(user,session)
    c.execute('INSERT INTO sessions (user, session) VALUES (?,?)', s)
  else:
    # Update current session
    s=(session,user)
    c.execute('UPDATE sessions SET session=? WHERE user=?',s)

  conn.commit()
  conn.close()

  return session

def check_session(user, session):
  session_stored = read_session(user)
  return (session_stored == session)

def read_user(session):
  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()

  s = (session,)
  c.execute('SELECT * FROM sessions WHERE session=?', s)
  row = c.fetchone()
  conn.close()

  if row == None:
    return None

  return row[0]

def read_session(user):
  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()

  # Try to get old session
  t = (user,)
  c.execute('SELECT * FROM sessions WHERE user=?', t)
  row = c.fetchone()
  conn.close()

  if row == None:
    return None

  return row[1]

def create_cookie(session):
  expir = datetime.datetime.now() + datetime.timedelta(hours=3)
  cookie = Cookie.SimpleCookie()
  cookie["session"] = session;
  cookie["session"]["domain"] = "data.cs.purdue.edu"
  cookie["session"]["path"] = "/"
  cookie["session"]["expires"] = expir.strftime("%a, %d-%b-%Y %H:%M%S EST")

  return cookie

def create_cleared_cookie():
  cookie = Cookie.SimpleCookie()
  cookie["session"] = ""
  cookie["session"]["domain"] = "data.cs.purdue.edu"
  cookie["session"]["path"] = "/"
  cookie["session"]["expires"] = 'Thu, 01 Jan 1970 00:00:00 GMT'

  return cookie

def session_from_cookie(cookie):
  return cookie["session"].value