__author__ = 'Daniel'
"""
This program takes a picture of the screen every time the PrtScreen class is built. It is used by the streaming client
because it takes a picture of the screen and converts it to jpeg format without having to save the picture on the
client's computer using StringIO.
"""
import ImageGrab
import cStringIO
JPEG_FORMAT = "jpeg"


class PrtScreen(object):
    """
    Basically takes a picture of the screen each time a PrtScreen object is made. Encodes the picture to JPEG format.
    Used with a generator to keep yielding pictures of the screen and sending them to the server.
    """
    def __init__(self):
        """
        Takes a picture of the screen, encodes it to jpeg format and saves it as a StringIO.
        """
        img = ImageGrab.grab()
        output = cStringIO.StringIO()
        img.save(output, format=JPEG_FORMAT)
        self.image = output.getvalue()
        output.close()

    def get_image(self):
        return self.image