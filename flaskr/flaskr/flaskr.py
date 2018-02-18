'''Passwords should never be stored in plain text in a production system. 
This project uses plain text passwords for simplicity. Normally,
passwords should be both hashed and salted before being stored in a database or file.'''

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

#Create the application instance
app = Flask(__name__)
#Load 'config' from this file itself
app.config.from_object(__name__)

#Load default 'config'
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'flask.db'),
    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'default'
))
#Override 'config' by loading a separate, environment-specific configuration file
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    '''Connects to the specified database using SQLite. Then the 
    sqlite3.Row object represents rows using dictionaries
    instead of tuples.'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    '''Opens a new database connection if there is none yet for the
    current application context.'''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    '''Script to initialize the database (does not initialize 
    the database by itself).'''
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

#The flask.Flask.cli.command() decorator registers a new command with the flask script.\
#When the command executes, Flask will automatically create an application\
#context which is bound to the right application
@app.cli.command('initdb')
def initdb_command():
    '''Initializes the database using the "initdb" flask command and 
    the 'init_db' function.'''
    init_db()
    print('Initialized the database.')

#The flask.Flaks.teardown_appcontext decorator makes sure the following function is called\
#every time the app context tears down (that is, either everything went well\
#or an exception happened, in which case the error is passed to the teardown function)
@app.teardown_appcontext
def close_db(error):
    '''Closes the database again at the end of the request.'''
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

#The flask.Flask.route() decorator is used to register a view function for a given\
#URL rule. 
#It is decorator equivalent to flask.Flask.add_url_rule()
@app.route('/')
def show_entries():
    '''The View function. Shows all the entries stored in the database.
    The one with the highest id (the newest entry) will be on top.
    It will pass entries to the 'show_entries.html' template and 
    return the rendered one.'''
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    '''Add new entry. This view lets the user add new entries if they are
    logged in; only responds to POST requests.'''
    #Test if the user is logged in (test if the 'logged_in' key is present and True)
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    #Use a parameterized SQL statement (i.e. placeholders instead of SQL literals) to protect\
    #against SQL injection attacks; qmark style
    db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Logs the user in. If either the username or the password are incorrect
    then the error variable will be updated; if the credentials are correct
    the user is logged in successfully and the 'logged_in' key created and
    assigned to True'''
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    '''Logs the user out (removes the 'logged_in' key).
    By passing a second parameter to pop(), the method will delete the key from
    the dictionary if present or do nothing if the key is not present. This means
    it's not needed to check if the user was logged in.'''
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
