import sqlite3
import hashlib
import Cookie
import cgi, string, sys, os, re, random
import cgitb; cgitb.enable()  # for troubleshooting
from subprocess import call
import time, datetime
import shutil
from operator import attrgetter

MYLOGIN="jselbo"
DATABASE="/homes/"+MYLOGIN+"/PeteTwitt/JTwitter.db"
IMAGEPATH="/homes/"+MYLOGIN+"/PeteTwitt/images"

HTML_HEADER = "Content-Type: text/html"

MAIL_STR = """Thank you for making an account on JTwitter!

To activate your account, copy and paste this link:
"""

TIME_FORMAT = '%A, %B %d, %Y at %H:%M'

# used in hashing activation email passwords
HASH_SALT = "B72A56138A3CF"

# used in hashing passwords 
PW_SALT = "A7242391634303FB9C83"

# html pages
LOGIN = 'login.html'
REGISTER = 'register.html'
HOME = 'home.html'
UPLOAD = 'upload.html'
EDIT_PROFILE = 'edit_profile.html'
SEARCH = 'search.html'

class Tweet:
    def __init__(self, tweet_id, owner, text, time):
        self.tweet_id = tweet_id
        self.owner = owner
        self.text = text
        self.time = time


def echo_html(html_file, dict={}, cookie=None):
    print(HTML_HEADER)
    if cookie is not None:
        print cookie.output()
    print

    with open(html_file, "r") as f:
        html = f.read()

        reg = re.compile('\$\{([^\}]+)\}')
        match = reg.search(html)
        while match is not None:
            match_name = match.groups()[0]
            replacement = dict.get(match_name, "")
            html = html[:match.start()] + replacement + html[match.end():]
            match = reg.search(html)
        
        print(html)

def echo_redirect(location, cookie=None):
    if cookie is not None:
        print cookie.output()
    print("Status: 303 See other")
    print("Location: {}".format(location))
    print

def echo_cookie(cookie):
    print cookie.output()

def send_activation_email(user):
    # calculate sha1 hash
    pwhash = hashlib.sha1(user + HASH_SALT).hexdigest()

    # write to temp file
    filename = 'mailtmp'
    with open(filename, 'w') as f:
        f.write(MAIL_STR)
        url = "http://data.cs.purdue.edu:9444/PeteTwitt/login.cgi?user={0}&activate={1}".format(user, pwhash)
        f.write(url)

    # send email
    f = open(filename)
    call(["/usr/bin/mailx", "-s", "JTwitter Activation", user], stdin=f)

def register_user(user, pw):
    conn = sqlite3.connect(DATABASE)

    pw = hashlib.sha1(pw + PW_SALT).hexdigest()

    # insert the user as unactivated
    vals = (user, pw, 0)
    conn.execute('INSERT INTO users (email, password, activated) VALUES(?,?,?)', vals)
    conn.commit()

    conn.close()

    # now, send email to that user that has a link to activation
    send_activation_email(user)

def check_user(user):
    conn = sqlite3.connect(DATABASE)
    curs = conn.cursor()

    curs.execute('SELECT * FROM users WHERE email=?', (user,))
    row = curs.fetchone()
    conn.close()

    return (row is not None)

def check_password(user, passwd):
    passwd = hashlib.sha1(passwd + PW_SALT).hexdigest()

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    t = (user,)
    c.execute('SELECT * FROM users WHERE email=?', t)

    row = stored_password = c.fetchone()
    conn.close()

    if row != None:
        # check password
        stored_password = row[1]
        if stored_password != passwd:
            return "failed"
        
        # check activation
        activated = row[2]
        if activated != 1:
            return "unactivated"

        return "passed"

    return "failed"

def activate_user(user, code):
    pwhash = hashlib.sha1(user + HASH_SALT).hexdigest()
    if pwhash != code: return False

    conn = sqlite3.connect(DATABASE)
    curs = conn.cursor()

    curs.execute('UPDATE users SET activated=1 WHERE email=?', (user,))
    conn.commit()
    conn.close()
    return True

def post_tweet(user, tweet):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    time = datetime.datetime.now().strftime(TIME_FORMAT)
    t = (user, tweet, time)
    c.execute('INSERT INTO tweets (owner, tweet, time) VALUES(?,?,?)', t)

    conn.commit()
    conn.close()

def sort_tweets(tweets):
    tweets.sort(key=attrgetter('time'), reverse=True)

def load_tweet(tweet_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('SELECT * FROM tweets WHERE id=?', (tweet_id,))
    row = c.fetchone()

    t = time.strptime(row[3], TIME_FORMAT)
    tw = Tweet(row[0], row[1], row[2], t)

    conn.close()

    return tw

def load_tweets(user):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('SELECT * FROM tweets WHERE owner=?', (user,))
    rows = c.fetchall()
    tweets = []
    for row in rows:
        t = time.strptime(row[3], TIME_FORMAT)
        tw = Tweet(row[0], row[1], row[2], t)
        tweets.append(tw)

    search = '%' + user + '%'
    c.execute('SELECT * FROM tweets WHERE tweet LIKE ?', (search,))
    rows = c.fetchall()
    for row in rows:
        t = time.strptime(row[3], TIME_FORMAT)
        tw = Tweet(row[0], row[1], row[2], t)
        tweets.append(tw)

    conn.close()

    return tweets

def generate_tweet_html(tweet, avatar):
    html = '<div class="tweet">'
    html += '<img src="{}" width="80" height="80" alt="{}"/>'.format(avatar, tweet.owner)
    html += '<div style="font-weight:bold">{}</div>'.format(tweet.owner)
    html += cgi.escape(tweet.text, True).replace('\n', '<br />')
    html += "<br />"
    html += "<h6>{}</h6>".format(time.strftime(TIME_FORMAT, tweet.time))
    html += '<form method="POST" action="home.cgi">'
    html += '<input type="hidden" name="reply" value={} />'.format(tweet.tweet_id)
    html += '<input type="submit" value="Reply" />'
    html += '</form>'
    html += '</div>'
    return html

def upload_avatar(user, f):
    # TODO generate random file name?

    fName, fExt = os.path.splitext(f.filename)
    dest = user + fExt
    destFile = os.path.expanduser('~/apache/htdocs/images/avatars/' + dest)

    if os.path.isfile(destFile):
        os.remove(destFile)
    with open(destFile, 'wb+', 0) as df:
        df.write(f.file.read())

    # now, insert in database
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE users SET avatar_path=? WHERE email=?', (dest, user))
    conn.commit()
    conn.close()

def load_avatar(user):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=?', (user,))
    row = c.fetchone()
    if row is None or row[3] is None: # use placeholder
        avatar = "../images/avatar-placeholder.gif"
    else:
        fn = row[3]
        avatar = '../images/avatars/' + fn

    conn.close()

    return avatar

def search_users(search):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    s = ('%'+search+'%',)
    c.execute('SELECT * FROM users WHERE email LIKE ?', s)

    users = []
    rows = c.fetchall()
    for row in rows:
        avatar = ""
        if row[3] is None:
            avatar = "../images/avatar-placeholder.gif"
        else:
            avatar = '../images/avatars/' + row[3]
        users.append((row[0], avatar))

    conn.close()
    return users

def generate_result_html(user):
    html = '<table class="result">'
    html += '<tr>'

    html += '<td>'
    html += '<img src="{}" width="80" height="80" alt="{}" />'.format(user[1], user[0])
    html += '</td>'

    html += '<td>'
    html += '<h5>'+user[0]+'</h5>'
    html += '<form method="link" action="search.cgi">'
    html += '<input type="submit" value="Subscribe" />'
    html += '<input type="hidden" name="subscribe" value="{}"/>'.format(user[0])
    html += '</form>'
    html += '</td>'

    html += '</tr>'
    html += '</table>'
    html += '<br />'
    return html

def get_subscriptions(user):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM subscriptions WHERE subscriber=?', (user,))

    users = []
    rows = c.fetchall()
    for row in rows:
        users.append(row[2])

    conn.close()
    return users

def subscribe_user(subscriber, user):
    if (subscriber == user):
        return False

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('SELECT * FROM subscriptions WHERE subscriber=? AND user=?', (subscriber, user))
    if c.fetchone() is None: # not subscribed yet
        c.execute('INSERT INTO subscriptions (subscriber, user) VALUES(?,?)', (subscriber, user))

    conn.commit()
    conn.close()
    return True

def change_password(user, newpw):
    conn = sqlite3.connect(DATABASE)

    newpw = hashlib.sha1(newpw + PW_SALT).hexdigest()

    # insert the user as unactivated
    vals = (newpw, user)
    conn.execute('UPDATE users set password=? WHERE email=?', vals)
    conn.commit()

    conn.close()