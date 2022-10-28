# Author: Andrea Gregorini

# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
#
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.
import threading
import multiprocessing

from djitellopy import Tello
import cv2, math, time


class drone(object):
    def __init__(self, name):
        self.name = name
        self.tello = Tello()
        self.button = 0

    def run(self):
        self.tello.connect()
        self.tello.streamon()
        self.tello.takeoff()
        while True:
            if self.button == 27:  # ESC
                break
            elif self.button == ord('w'):
                self.tello.move_forward(30)
            elif self.button == ord('s'):
                self.tello.move_back(30)
            elif self.button == ord('a'):
                self.tello.move_left(30)
            elif self.button == ord('d'):
                self.tello.move_right(30)
            elif self.button == ord('e'):
                self.tello.rotate_clockwise(30)
            elif self.button == ord('q'):
                self.tello.rotate_counter_clockwise(30)
            elif self.button == ord('r'):
                self.tello.move_up(30)
            elif self.button == ord('f'):
                self.tello.move_down(30)
        self.tello.land()
        self.tello.streamoff()

    def get_image(self):
        frame_read = self.tello.get_frame_read()
        while True:
            img = frame_read.frame
            cv2.imshow("drone", img)
            self.button = cv2.waitKey(1) & 0xff
            if self.button == 27:
                break
        cv2.destroyAllWindows()


def multiprocessing_guide(i, drone_1):
    if i == 0:
        drone_1.run()
    if i == 1:
        drone_1.get_image()


if __name__ == '__main__':
    drone_1 = drone("Name")
    guide = threading.Thread(target=multiprocessing_guide,
                                    args=(0, drone_1))
    image = threading.Thread(target=multiprocessing_guide,
                                    args=(1, drone_1))
    guide.start()
    image.start()
