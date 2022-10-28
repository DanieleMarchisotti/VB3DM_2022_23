#  Smart Robot Car V4.0 Elegoo Python Demo
# This demo is an example of how the wifi communication between ESP32 (Smart Robot Car V4.0 Elegoo) and PC should be
# set.
# The communication between ESP32 (Smart Robot Car V4.0 Elegoo) and PC is based on 3 parts:
# 1. Heartbeat: when the connection is started (line in the code: self.sock.connect(("192.168.4.1", UDP_PORT))), the
#    PC must sent a message to the ESP32 containing "{Heartbeat}" every second. Otherwise, ESP32 that acts as a server
#    interrupts the connection;
# 2. Image: the image is sent by the ESP32 to the URL "http://192.168.4.1/Test" and it must be read from it;
# 3. Commands: the PC sends coded messages as the one contained in the communication example file
#    "robot_car_example_messages.txt" to control the movement of the car
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


class Controller(object):  # controller class
    def __init__(self, name):  # init method: executed when an object fo the class Controller is created
        self.name = name
        self.k = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # set up UDP
        self.sock.connect(("192.168.4.1", UDP_PORT))

    def run(self):
        delay = 0.5
        status = 0
        while True:
            print(status)
            # if I press 'w', I send a command to the car to move straight
            if self.k == ord('w') and (status == 0 or status == 2):
                status = self.handle_action(Message.TOP.value, status)
            # if I press 'q', I send a command to the car to move straight-left
            if self.k == ord('q') and (status == 0 or status == 2):
                status = self.handle_action(Message.TOP_LEFT.value, status)
            # if I press 'a', I send a command to the car to turn left
            if self.k == ord('a') and (status == 0 or status == 2):
                status = self.handle_action(Message.LEFT.value, status)
            # if I press 'z', I send a command to the car to move back-left
            if self.k == ord('z') and (status == 0 or status == 2):
                status = self.handle_action(Message.BOTTOM_LEFT.value, status)
            # if I press 'x', I send a command to the car to move back
            if self.k == ord('x') and (status == 0 or status == 2):
                status = self.handle_action(Message.BOTTOM.value, status)
            # if I press 'c', I send a command to the car to move back-right
            if self.k == ord('c') and (status == 0 or status == 2):
                status = self.handle_action(Message.BOTTOM_RIGHT.value, status)
            # if I press 'd', I send a command to the car to turn right
            if self.k == ord('d') and (status == 0 or status == 2):
                status = self.handle_action(Message.RIGHT.value, status)
            # if I press 'e', I send a command to the car to move straight-right
            if self.k == ord('e') and (status == 0 or status == 2):
                status = self.handle_action(Message.TOP_RIGHT.value, status)
            # if I press 't', I send a command to the car to turn the camera to the left
            if self.k == ord('t') and (status == 0 or status == 2):
                status = self.handle_action(Message.CAMERA_LEFT.value, status)
            # if I press 't', I send a command to the car to turn the camera to the right
            if self.k == ord('y') and (status == 0 or status == 2):
                status = self.handle_action(Message.CAMERA_RIGHT.value, status)
            elif self.k == -1 and (status == 1 or status == 3):
                if status == 1:
                    status += 1
                else:
                    self.sock.send(Message.STOP.value)  # if I press 't', I send a command to the car to stop
                    status = 0
            elif self.k == 27:
                break

    def handle_action(self, action, status):
        # Function that sends a message to the ESP32 that correspond to a command
        if status == 0:
            status += 1
        else:
            self.sock.send(action)
            status += 1
        return status

    def get_image(self):
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
                    self.k = cv.waitKey(1)  # get key pressed on the keyboard by the user
            except Exception as e:
                print("Error:" + str(e))
                bts = b''
                stream = urlopen(url)
                continue
            if self.k == ord('p'):  # if I press p I save the image
                cv.imwrite(str(i) + ".jpg", img)
                i = i + 1
            if self.k == 27:  # end thread if I press esc on the image shown
                break
        cv.destroyAllWindows()

    def send_heartbeat(self):
        while True:
            self.sock.send(Message.BEAT.value)  # send heartbeat
            time.sleep(1)  # the thread wait 1 second
            if self.k == 27:  # end thread if I press esc on the image shown
                break


if __name__ == '__main__':

    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)

    ctrl = Controller("Vehicle_0")  # define the variable of the class Controller. When this line of code is executed,
    # the __init__ method of the controlled class is executed, that means the wifi connection starts.
    t_image = threading.Thread(target=ctrl.get_image, args=())  # define a thread used only to get images
    t_image.start()  # starting the thread to get images
    t_beat = threading.Thread(target=ctrl.send_heartbeat, args=())  # define a thread used to send heartbeat
    t_beat.start()  # starting the heartbeat thread
    t_ctrl = threading.Thread(target=ctrl.run, args=())  # define a thread used to send messages
    t_ctrl.start()  # starting the commands thread
