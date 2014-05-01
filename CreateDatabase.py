#!/usr/bin/python

import sqlite3
import os.path
import os

DB = 'JTwitter.db'

if os.path.isfile(DB):
	os.remove(DB)

conn = sqlite3.connect(DB)

c = conn.cursor()

# Turn on foreign key support
c.execute("PRAGMA foreign_keys = ON")

# Create users table
c.execute('''CREATE TABLE users
	     (email TEXT NOT NULL, 
	      password TEXT NOT NULL,
	      activated INTEGER,
	      avatar_path TEXT,
	      PRIMARY KEY(email))''')

c.execute('''CREATE TABLE tweets
          (id INTEGER,
           owner TEXT NOT NULL,
           tweet TEXT NOT NULL,
           time TEXT NOT NULL,
           FOREIGN KEY (owner) REFERENCES users(email),
           PRIMARY KEY(id))''')

c.execute('''CREATE TABLE subscriptions
			(id INTEGER,
			subscriber TEXT NOT NULL,
			user TEXT NOT NULL,
			FOREIGN KEY (subscriber) REFERENCES users(email),
			FOREIGN KEY (user) REFERENCES users(email),
			PRIMARY KEY(id))''')

# Create album table
# Visibility is 'public' or 'private'
c.execute('''CREATE TABLE albums
	     (name TEXT NOT NULL,
	      owner TEXT NOT NULL,
	      visibility TEXT NOT NULL,
	      FOREIGN KEY (owner) REFERENCES users(email),
	      PRIMARY KEY(name, owner))''')

# Create pictures table
c.execute('''CREATE TABLE pictures
	     (path TEXT NOT NULL,
	      album TEXT NOT NULL,
	      owner TEXT NOT NULL,
	      FOREIGN KEY(album, owner) REFERENCES albums(name, owner),
	      FOREIGN KEY(owner) REFERENCES users(email),
	      PRIMARY KEY(path))''')

# Create sessions table
c.execute('''CREATE TABLE sessions
	     (user TEXT NOT NULL,
	      session TEXT NOT NULL,
	      FOREIGN KEY(user) REFERENCES users(email),
	      PRIMARY KEY(session))''')


            ]

albums = [("album1",'george@gmail.com',"public"),
           ("album2",'george@gmail.com',"public"),
           ("album3",'george@gmail.com',"private"),
           ("album1",'mary@gmail.com',"public"),
         ]
c.executemany('INSERT INTO albums VALUES (?,?,?)', albums)

# Save the changes
conn.commit()

# Close the connection
conn.close()
