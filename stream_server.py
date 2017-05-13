__author__ = 'Daniel'
"""
This is the streaming website server. It uses the flask and gevent modules to create a multi client server where clients
can watch users stream their screens live. You can sign up to the website, therefore creating your own user page on the
website.
"""
from gevent.pywsgi import WSGIServer
from image_receive_server import ImageReceiveServer, USER_STREAM_IMAGES, username_in_db
import threading
from flask import Flask, render_template, Response, url_for, request, redirect
from flask_login import LoginManager, login_user, login_required, current_user
import os
import sqlite3
from user_class import User
RECEIVE_SIZE = 500000
CURRENT_WORKING_DIRECTORY = os.getcwd()  # Gives easy access to our server's files' path.
STREAM_CLIENT_USERNAME_PARAMETER = 'username:'
NEW_LINE = '\n'
USERNAME_START_INDEX = 10
USERNAME_ELEMENT = 1
BACKLOG = 5
NEWEST_IMAGE = -1
IMAGE_BEFORE_THE_NEWEST = -2
EXTENSION_ELEMENT = 1
CODE_FILES_PATH = CURRENT_WORKING_DIRECTORY + '\\Templates\\'  # The path to where all the server files are saved at
DEFAULT_IMAGE = CODE_FILES_PATH + 'duck.jpg'
MIMETYPES = {'css': 'text/css'}
FRAME_DATA = b'--frame\r\n'\
             b'Content-Type: image/jpeg\r\n\r\n' + '%s' + b'\r\n'
USERNAME_ELEMENT = 'username'
PASSWORD_ELEMENT = 'password'
DB_PATH = CODE_FILES_PATH + 'userbase.db'
WEB_SERVER_PORT = 5000
ABOUT_USER = 'about'
USER_AGE = 'age'
USER_SEX = 'sex'
USER_FAVORITE_FOOD = 'favorite_food'
MULTIPART_MIMETYPE = 'multipart/x-mixed-replace; boundary=frame'
DEFAULT_INFO = ""

# Starts the flask app.
app = Flask(__name__)
app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    """
    Renders the homepage.
    """
    return render_template('index.html')


@app.route('/submit_login', methods=['POST'])
def submit_login():
    """
    Extracts the username and password inserted by the user. Checks if the user exists in the database and if he does
    checks if the password that was inserted by the user is correct.
    """
    username = request.form[USERNAME_ELEMENT]
    password = request.form[PASSWORD_ELEMENT]
    if validate_login(username, password):
        user = User(username, password)
        login_user(user)
        return render_template('successful_login.html')
    return render_template('log_in.html')


def validate_login(username, password):
    """
    username: String: the username of the user
    password: String: the password that the user entered.

    Validates if the username and password belong to an existing user and are both correct. Returns True if the user
    has been validated and False otherwise.
    """
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (username,))
    password2 = cur.fetchone()
    db.close()
    if password2 is None:
        return False
    if password2[0] == password:
        return True
    return False


@app.route('/edit_profile')
@login_required
def edit_profile():
    """
    Renders the page that allows a logged in user to change the information about himself.
    """
    return render_template('edit_profile.html')


@app.route('/change_profile', methods=['POST'])
@login_required
def change_profile():
    """
    Updates the logged in user's profile according to the new information he gave.
    """
    about = request.form[ABOUT_USER]
    age = request.form[USER_AGE]
    sex = request.form[USER_SEX]
    favorite_food = request.form[USER_FAVORITE_FOOD]
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("UPDATE users SET about=?, age=?, sex=?, favorite_food=? WHERE username=?", (about, age, sex, favorite_food, current_user.id))
    db.commit()
    db.close()
    return redirect(url_for('generate_user_page', username=current_user.id))


@login_manager.user_loader
def user_loader(user_id):
    """
    user_id: unicode: username used to make the corresponding User object

    Given *user_id*, return the associated User object.
    this is set as the user_loader for flask-login. It uses it to retrieve a User object which it then uses for
    everything.
    if no user can be made (e.g invalid user_id), it returns None. (This is specified by flask-login as the type to
    return if no User object can be made)
    """
    return make_user(str(user_id))


def make_user(user_id):
    """
    user_id: String: username used to make the corresponding User object

    Given *user_id*, return the associated User object.
    Creates the User object associated with user_id. If no User object can be made, returns None.
    """
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (user_id,))
    password = cur.fetchone()
    db.close()
    if password is None:
        return None
    return User(user_id, password[0])


@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    """
    Extracts the username and password inserted by the user. Checks if the user already exists and if he doesn't, adds
    him to the user database.
    """
    username = request.form[USERNAME_ELEMENT]
    password = request.form[PASSWORD_ELEMENT]
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cur.fetchone()
    if user_data is None:  # Checks if the username inserted already exists in the database
        cur.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (username, password, DEFAULT_INFO, DEFAULT_INFO, DEFAULT_INFO, DEFAULT_INFO))
        db.commit()
        db.close()
        return render_template('successful_signup.html')
    else:
        print user_data
        db.close()
        return render_template('user_already_exists.html')


@app.route('/log_in')
def log_in():
    """
    Generates the log in page.
    """
    return render_template('log_in.html')


@app.route('/submit_file/<filename>')
def return_files(filename):
    """
    :filename: String: the name of the file that is requested by the browser.

    returns the file requested by the browser to the browser.
    """
    file_path = CODE_FILES_PATH + filename  # All of the web server's files are in CODE_FILES_PATH
    print file_path
    if os.path.isfile(file_path):
        print file_path
        with open(file_path, 'rb') as web_file:
            file_extension = os.path.splitext(file_path)[EXTENSION_ELEMENT]
            file_extension = file_extension.strip('.')  # Strips the file extension's redundant '.' in the beginning
            mimetype = MIMETYPES[file_extension]
            file_data = web_file.read()
            return Response(file_data + b'\r\n', mimetype=mimetype)
    return render_template('file_not_found.html')


@app.route('/video_feed/<username>')
def video_feed(username):
    """
    username: String: a String of the user page requested in the url.
    every time video_feed gets called, it returns the newest frame of the stream of the specific username requested
    and updates the video feed for the client.
    """
    return Response(gen(username), mimetype=MULTIPART_MIMETYPE)


def gen(username):
    """
    username: String: a String of the user page requested in the url.

    every time gen is called, it yields the most recent frame of the video feed of : username :
    """
    frame = open(DEFAULT_IMAGE, 'rb').read()  # Initial default image to show in case the user isn't currently streaming
    while True:
        try:
            if username in USER_STREAM_IMAGES.keys():
                frame = USER_STREAM_IMAGES[username][NEWEST_IMAGE]
                yield (FRAME_DATA % frame)
            else:
                yield (FRAME_DATA % frame)
        except IndexError:
            yield (FRAME_DATA % frame)


@app.route('/user/<username>')
def generate_user_page(username):
    """
    username: String: a String of the user page requested in the url.
    generates the requested user page if it exists, if not, generates the page saying that the user was not found.
    """
    if username_in_db(username):
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        cur.execute("SELECT about, age, sex, favorite_food FROM users WHERE username=?", (username,))  # Retrieves the info about the user.
        row = cur.fetchone()
        about, age, sex, favorite_food = row
        return render_template('video_feed.html', video_url=url_for('video_feed', username=username), about=about, age=age, sex=sex, favorite_food=favorite_food)
    return render_template('user_not_found.html')


if __name__ == "__main__":
    print CODE_FILES_PATH
    thread = threading.Thread(target=ImageReceiveServer().start_server)
    thread.daemon = True
    thread.start()
    app.config["SECRET_KEY"] = "ITSASECRET"
    http = WSGIServer(('', WEB_SERVER_PORT), app)
    http.serve_forever()
