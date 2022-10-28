#  Smart Robot Car V4.0 Elegoo Python Demo
# This demo is an example of how the wifi communication between ESP32 (Smart Robot Car V4.0 Elegoo) and PC should be
# set.
# The communication between ESP32 (Smart Robot Car V4.0 Elegoo) and PC is based on 3 parts:
# 1. Heartbeat: when the connection is started (line in the code: self.sock.connect(("192.168.4.1", UDP_PORT))), the
#    PC must sent a message to the ESP32 containing "{Heartbeat}" every second. Otherwise, ESP32 that acts as a server
#    interrupts the connection;
# 2. Image: the image is sent by the ESP32 to the URL "http://192.168.4.1/Test" and it must be read from it;
# 3. Commands: in the main program, to send commands as going forward and going back
# These 3 parts run simultaneously on your PC, that means they run on different threads.


import socket  # library to start wifi communication
import threading  # library to start multiple threads on your PC (multiple parts of codes, for example loops, running
# simultaneously

import cv2 as cv  # import opencv
from urllib.request import urlopen  # import library to read the image of the car at the URL "http://192.168.4.1/Test"
import numpy as np
from enum import Enum  # library to define a struct variable
import time

UDP_IP = "192.168.4.1"    # server ip address for UDP protocol communication
UDP_PORT = 5353  # UDP port communication
power = b"125"  # power at which the motors of the car are running
k = 0


class Message(Enum):  # variable containing messages to be sent to the car
    TOP = b"{\n  \"N\": 102,\n  \"D1\": 1,\n  \"D2\": " + power + b"\n}"
    BOTTOM = b"{\n  \"N\": 102,\n  \"D1\": 2,\n  \"D2\": " + power + b"\n}"
    LEFT = b"{\n  \"N\": 102,\n  \"D1\": 3,\n  \"D2\": " + power + b"\n}"
    RIGHT = b"{\n  \"N\": 102,\n  \"D1\": 4,\n  \"D2\": " + power + b"\n}"
    TOP_LEFT = b"{\n  \"N\": 102,\n  \"D1\": 5,\n  \"D2\": " + power + b"\n}"
    TOP_RIGHT = b"{\n  \"N\": 102,\n  \"D1\": 7,\n  \"D2\": " + power + b"\n}"
    BOTTOM_LEFT = b"{\n  \"N\": 102,\n  \"D1\": 6,\n  \"D2\": " + power + b"\n}"
    BOTTOM_RIGHT = b"{\n  \"N\": 102,\n  \"D1\": 8,\n  \"D2\": " + power + b"\n}"
    CAMERA_LEFT = b"{\n  \"N\": 106,\n  \"D1\": 3,\n  \"D2\": " + power + b"\n}"
    CAMERA_RIGHT = b"{\n  \"N\": 106,\n  \"D1\": 4,\n  \"D2\": " + power + b"\n}"
    STOP = b"{\n  \"N\": 102,\n  \"D1\": 9,\n  \"D2\": 0\n}"
    BEAT = b"{Heartbeat}"


def get_image():
    global k  # global variable to end the thread
    url = "http://192.168.4.1/Test"
    CAMERA_BUFFRER_SIZE = 4096
    stream = urlopen(url)
    bts = b''
    i = 0
    while True:
        try:
            bts += stream.read(CAMERA_BUFFRER_SIZE)  # get image
            jpghead = bts.find(b'\xff\xd8')  # get initial part of the image
            jpgend = bts.find(b'\xff\xd9')  # get final part of the image
            if jpghead > -1 and jpgend > -1:
                jpg = bts[jpghead:jpgend + 2]
                bts = bts[jpgend + 2:]
                img = cv.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv.IMREAD_UNCHANGED)
                img = cv.resize(img, (640, 480))
                cv.imshow("Image", img)  # open a figure called "Image" and show the image from ESP32
                k = cv.waitKey(1)  # get key pressed on the keyboard by the user
        except Exception as e:
            print("Error:" + str(e))
            bts = b''
            stream = urlopen(url)
            continue
        # if k == ord('p'):  # if I press p I save the image
        #     cv.imwrite(str(i) + ".jpg", img)
        #     i = i + 1
        if k == 27:  # end thread if I press esc on the image shown
            break
    cv.destroyAllWindows()


def send_heartbeat():
    global k  # global variable to end the thread
    while True:
        sock.send(Message.BEAT.value)  # send heartbeat
        time.sleep(1)  # the thread wait 1 second
        if k == 27:
            break


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # set up UDP
    sock.connect(("192.168.4.1", UDP_PORT))
    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)

    t_image = threading.Thread(target=get_image, args=())  # define a thread used only to get images
    t_image.start()  # starting the thread to get images
    t_beat = threading.Thread(target=send_heartbeat, args=())  # define a thread used to send heartbeat
    t_beat.start()  # starting the heartbeat thread
    # example of commands to send to the car
    sock.send(Message.TOP.value)
    time.sleep(1)
    sock.send(Message.STOP.value)
    time.sleep(1)
    sock.send(Message.BOTTOM.value)
    time.sleep(1)
    sock.send(Message.STOP.value)
