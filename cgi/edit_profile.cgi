#!/usr/bin/python

import cgi
from util import *
import session

try:
	cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
	sess = session.session_from_cookie(cookie)
	user = session.read_user(sess)

	opts = {'user': user}

	# get avatar
	avatar = load_avatar(user)
	opts['avatar'] = avatar

	# get tweets
	tweets = load_tweets(user)
	sort_tweets(tweets)

	if len(tweets) > 0:
		tweet_html = ""
		for tweet in tweets:
			tweet_html += generate_tweet_html(tweet, avatar)
		opts['tweets'] = tweet_html
	else:
		opts['tweets'] = "<h5>You have no tweets!</h5>"

	form = cgi.FieldStorage()

	if "action" in form and form["action"].value == "upload_avatar":
		if "image" in form and form["image"].file:
			f = form["image"]
			upload_avatar(user, f)
	elif "action" in form and form["action"].value == "change_password":
		if "password_field" in form:
			pw = form["password_field"].value
			change_password(user, pw)
			opts["message"] = "Password changed succesfully."

	echo_html(EDIT_PROFILE, opts)
except (Cookie.CookieError, KeyError):
	# not logged in yet
	echo_redirect("login.cgi")