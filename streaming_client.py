__author__ = 'Daniel'
"""
This is a program for clients for streaming their screens to the server using jpeg motion.
"""
import socket
from image_taker import PrtScreen
SERVER_IP_AND_PORT = '127.0.0.1', 8888
END = False
INSERT_USERNAME_MESSAGE = "Insert your username\n"
INFO_MESSAGE = 'Enter Ctrl + C to safely exit, If you do not safely exit the program, PROBLEMS WILL HAPPEN (DONT PRESS X)'
PROGRAM_END_MESSAGE = 'If you did not Enter Ctrl + C, then the server kicked you for some reason\n(invalid username?)'


def send_pictures(server_socket, user_name):
    """
    server_socket: Socket object: the server's socket.
    user_name: String: The username inserted by the user.
    Sends the server the stream of pictures to create the jpeg motion. puts the user's username in the start of each
    packet so the server knows on which user page to display the image stream on.
    """
    user_info = 'username: ' + user_name + '\n'
    print INFO_MESSAGE
    while True:
        try:
            frame = PrtScreen().get_image()
            data_packet = user_info + frame
            server_socket.send(data_packet)
        except (KeyboardInterrupt, socket.error):
            server_socket.close()
            print PROGRAM_END_MESSAGE
            break


if __name__ == "__main__":
    username = raw_input(INSERT_USERNAME_MESSAGE)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_IP_AND_PORT)
    send_pictures(sock, username)
