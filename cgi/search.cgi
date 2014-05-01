#!/usr/bin/python

import cgi
from util import *
import session

try:
	cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
	sess = session.session_from_cookie(cookie)
	user = session.read_user(sess)

	form = cgi.FieldStorage()

	results_html = ""
	message = ""

	if "action" in form and form["action"].value == "search":
		if "search_field" in form:
			search = form["search_field"].value
			results = search_users(search)
			if len(results) > 0:
				for result in results:
					results_html += generate_result_html(result)
	elif "subscribe" in form:
		sub_user = form["subscribe"].value
		if subscribe_user(user, sub_user):
			message = "You have succesfully subscribed to " + sub_user + "."
		else:
			message = "Could not subscribe to user " + sub_user + "."


	echo_html(SEARCH, {'user': user, 'results': results_html, 'message': message})
except (Cookie.CookieError, KeyError):
	# not logged in yet
	echo_redirect("login.cgi")