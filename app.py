from flask import Flask, url_for, redirect, render_template, request
import grader
import argparse
import os
import string
from random import sample, choice
import hashlib
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

app = Flask(__name__)

###################
## CONFIGURATION ##
###################
RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
DB = 'instabase'


### initialize the validator
validator = grader.createValidator("data/gold.csv")

###################
###### UTILS ######
###################
def generate_password(uni,length=18):
    chars = string.letters + string.digits
    rand_pass = ''.join([choice(chars) for i in range(8)])
    sha = hashlib.sha1(uni).hexdigest()
    return sha[:10] + rand_pass

def is_columbia_email(email):
    email = email.strip()
    return email and email.split('@')[-1] == "columbia.edu"


####################
####### DB #########
####################
def db_setup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(DB).run(connection)
        r.db(DB).table_create('leaderboard').run(connection)
        r.db(DB).table_create('submissions').run(connection)
        r.db(DB).table_create('users').run(connection)
        print 'Database setup completed. Now run the app without --setup.'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup.'
    finally:
        connection.close()

def db_drop():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_drop(DB).run(connection)
        print "Database dropped."
    except:
        print "Error in dropping database"
    finally:
        connection.close()

@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass


####################
#### ROUTES ########
####################
@app.route('/')
def dashboard():
    return "this is the dashboard"

@app.route('/leaderboard')
def leaderboard():
    return "this is the leaderboard"

@app.route('/signup', methods=["POST"])
def signup():
    email = request.form.get('email')
    if not is_columbia_email(email):
        print "not a valid columbia email"
    else:
        password = generate_password(email)
        print email, password
    return redirect(url_for('login'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == "test@columbia.edu" and password == "123":
            return redirect(url_for('dashboard'))
    return render_template("login.html")

if __name__  == "__main__":
    parser = argparse.ArgumentParser(description='Run the instabase app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')
    parser.add_argument('--drop', dest='run_drop', action='store_true')
    args = parser.parse_args()
    if args.run_setup:
        db_setup()
    elif args.run_drop:
        db_drop()
    else:
        app.run(debug=True)
