#!/usr/bin/python

import cgi
from util import *
import session

try:
	cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
	sess = session.session_from_cookie(cookie)
	user = session.read_user(sess)

	msg = ""
	tweet_text = ""

	form = cgi.FieldStorage()
	if "action" in form and form["action"].value == "tweet":
		tweet = form["tweet_field"].value
		post_tweet(user, tweet)

		msg = "Tweet posted succesfully!"
	elif "reply" in form:
		tweet_id = form["reply"].value
		tweet = load_tweet(tweet_id)
		tweet_text = 'Reply to {} "{}":\n\n'.format(tweet.owner, tweet.text)

	tweets = []
	subs = get_subscriptions(user)
	for sub in subs:
		tweets_sub = load_tweets(sub)
		tweets.extend(tweets_sub)
		#msg += sub + "<br />"

	sort_tweets(tweets)

	tweet_html = ""

	if len(tweets) > 0:
		for tweet in tweets:
			avatar = load_avatar(tweet.owner)
			tweet_html += generate_tweet_html(tweet, avatar)
	else:
		tweet_html = "No tweets to show... :("

	echo_html(HOME, {'user': user, 'message': msg, 'tweets': tweet_html, 'tweet_text': tweet_text})
except (Cookie.CookieError, KeyError):
	# not logged in yet
	echo_redirect("login.cgi")