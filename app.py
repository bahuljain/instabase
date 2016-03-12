from flask import Flask, url_for, redirect, render_template, request
import grader
import string
from random import sample, choice
import hashlib

app = Flask(__name__)

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
    app.run(debug=True)
