#!/usr/bin/python

import cgi
from util import *

form = cgi.FieldStorage()

if "action" in form and form["action"].value == "register":
    if "username" in form and "password" in form:
        username = form["username"].value
        password = form["password"].value

        # first, check if user already exists
        if check_user(username):
            echo_html(REGISTER, {'error': 'That user already exists.'})
        else:
            register_user(username, password)

            echo_html(LOGIN, {'message': 'Your account was succesfully created. Please check your email to activate.'})
    else:
        echo_html(REGISTER, {'error': 'Please fill out all fields.'})
else:
    echo_html(REGISTER)
