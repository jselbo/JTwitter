#!/usr/bin/python

import Cookie
from util import *
import session

set_cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
cookie = session.create_cleared_cookie()

echo_redirect("login.cgi", cookie)