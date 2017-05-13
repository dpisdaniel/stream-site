__author__ = 'Daniel'
"""

"""
from flask_login import UserMixin
from image_receive_server import DB_PATH
import sqlite3


class User(UserMixin):
    """
    User class for the use of flask-login. flask-login demands a User class to be sent to some of its methods
    in order for flask-login to work. flask-login also needs the User class to have several mandatory properties
    which are taken from UserMixin.
    """
    database = sqlite3.connect(DB_PATH)
    cur = database.cursor()

    def __init__(self, username, password):
        """
        username: String: the username of the user.
        password: String: the password of the user.

        Builds a new user.
        """
        self.id = username
        self.password = password

    @classmethod
    def get(cls, user_id):
        """
        user_id: String: the user id that is used to retrieve the information about the requested user. a unique id

        Returns the information about the user that is user_id.
        """
        return cls.cur.execute("SELECT * FROM users WHERE username=?", (user_id,)).fetchall()