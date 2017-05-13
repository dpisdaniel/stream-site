__author__ = 'Daniel'
"""
This server is a multi client server that receives image streams from users that connect to it and allows the main
server to display them on each user's page.
"""
import select
import socket
import sqlite3
STREAM_RECEIVE_SERVER_IP_AND_PORT = '127.0.0.1', 8888
RECEIVE_SIZE = 500000
USER_STREAM_IMAGES = {}
DEFAULT_IMAGE = r'T:\downloads\duck.jpg'
STREAM_CLIENT_USERNAME_PARAMETER = 'username:'
NEW_LINE = '\n'
USERNAME_START_INDEX = 10
USERNAME_ELEMENT = 1
BACKLOG = 5
NEWEST_IMAGE = -1
DB_PATH = 't:/heights/documents/projects/streaming_site/templates/userbase.db'


def username_in_db(username):
    """
    username: String: the username that the client sent.
    Checks if :username: exists in our database, returns True if it does and False otherwise.
    """
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cur.fetchone()
    db.close()
    if user_data is not None:  # Checks if the user exists in the database.
        return True
    return False


class ImageReceiveServer():
    def __init__(self):
        """
        Initializes the image receive server's parameters.
        self.stream_recv_sock: Socket object: The server's socket.
        self.open_client_sockets: List object: A list of client sockets that currently have an open connection with the
        server
        self.open_clients_sockets_and_usernames: List of Tuples: Contains each client socket's corresponding username
        in a tuple form.
        """
        self.stream_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_recv_sock.bind(STREAM_RECEIVE_SERVER_IP_AND_PORT)
        self.open_client_sockets = []
        self.open_clients_sockets_and_usernames = []
        self.r, self.w, self.e = None, None, None

    def start_server(self):
        """
        Begins listening to clients on :socket :self.stream_recv_sock:
        """
        self.stream_recv_sock.listen(BACKLOG)
        while True:
            self.r, self.w, self.e = select.select([self.stream_recv_sock] + self.open_client_sockets, [], [])
            self._receive_pictures()

    def _is_new_client(self, curr_sock):
        """
        curr_sock: Socket object: the socket that the program is currently iterating over
        Checks if :curr_sock: is the socket of a new client and returns True if it is, False otherwise.
        """
        if curr_sock is self.stream_recv_sock:  # new client
            new_sock, address = self.stream_recv_sock.accept()
            self.open_client_sockets.append(new_sock)
            return True
        return False

    def _handle_new_image(self, image_part, current_sock):
        """
        image_part: String : contains a packet's data.
        current_sock: socket: the current checked socket.

        checks if :image_part: is the first part of a new image and the username sent with it is valid. If everything is
        valid, properly stores the image part in the correct dictionary value and returns True. If the username is not
        valid or :image_part: isn't a new image, returns False.
        """
        end_of_username_index = image_part.find(NEW_LINE)
        image_data_start_index = end_of_username_index + 1
        username = image_part[USERNAME_START_INDEX:end_of_username_index]
        if image_part.startswith(STREAM_CLIENT_USERNAME_PARAMETER) and username_in_db(username):
            if (current_sock, username) not in self.open_clients_sockets_and_usernames:
                self.open_clients_sockets_and_usernames.append((current_sock, username))
            if username not in USER_STREAM_IMAGES.keys():  # Checks if the user exists in our image stream dictionary
                USER_STREAM_IMAGES[username] = []
            image_data = image_part[image_data_start_index:]
            if len(USER_STREAM_IMAGES[username]) > 0:
                USER_STREAM_IMAGES[username].pop()  # takes out previous picture
            USER_STREAM_IMAGES[username].append(image_data)  # inserts the newly received picture_part
            return True
        return False

    def _handle_image_part(self, image_part, current_sock):
        """
        image_part: String : contains a packet's data.
        current_sock: socket: the current checked socket.

        checks to see if :image_part: is an image part of a client's previously sent message. If it is, concatenates
        :image_part: to the previously sent image part in the proper user dictionary value.
        If it isn't, closes the connection with the client since he sent irrelevant packet data.
        """
        username = ""
        for socket_user_tuple in self.open_clients_sockets_and_usernames:
            if current_sock in socket_user_tuple:
                username = socket_user_tuple[USERNAME_ELEMENT]
                USER_STREAM_IMAGES[username][NEWEST_IMAGE] += image_part
        if username == "":
            self.open_client_sockets.remove(current_sock)
            current_sock.close()

    def _receive_pictures(self):
        """
        Iterates over all the sockets that can be read, checks if they already have a connection with our server and if
        they do, receives the pictures from them.
        """
        for current_sock in self.r:
            if not self._is_new_client(current_sock):
                image_part = current_sock.recv(RECEIVE_SIZE)
                if not self._handle_new_image(image_part, current_sock):
                    self._handle_image_part(image_part, current_sock)
