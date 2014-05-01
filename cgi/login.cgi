#!/usr/bin/python

import cgi
from util import *
import session

form = cgi.FieldStorage()

if "user" in form and "activate" in form:
    if activate_user(form["user"].value, form["activate"].value):
        echo_html(LOGIN, {'message': 'Activation successful. Please login now.'})
    else:
        echo_html(LOGIN, {'error': 'Failed activation.'})
elif "action" in form and form["action"].value == "login":
    if "username" in form and "password" in form:
        username = form["username"].value
        password = form["password"].value
        valid = check_password(username, password)
        if valid == "passed":
            sess = session.create_session(username)
            cookie = session.create_cookie(sess)

            echo_redirect("home.cgi", cookie)
        elif valid == "failed":
            echo_html(LOGIN, {'error': 'Incorrect username or password'})
        elif valid == "unactivated":
            echo_html(LOGIN, {'error': 'Your account has not been activated yet.'})
    else:
        echo_html(LOGIN, {'error': 'Please enter a username and password'})
else:
    echo_html(LOGIN)