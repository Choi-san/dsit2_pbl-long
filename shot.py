# coding: utf-8
import os
import sys
import RPi.GPIO as GPIO
from time import sleep
import warnings
import cv2
import datetime
import configparser

warnings.simplefilter('ignore')

def set_ini(ini_path):
    config_file = ini_path
    inifile = configparser.ConfigParser()
    inifile.read(config_file, 'utf_8')
    return inifile

def kake(file):
    return 0

def dakon_kizu(file):
    return 0

def main():
    base_path = './pict/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '/'
    os.makedirs(base_path, exist_ok=True)
    capture = cv2.VideoCapture(0)
    config=set_ini('./config.ini')
    led_pos_list = ['front','right','left','back']
    GPIO.setmode(GPIO.BCM)

    for led_pos in led_pos_list:
        GPIO.setup(pin_num, GPIO.OUT)
        pin_num = config.getint('pin_number',led_pos)
        GPIO.output(pin_num, GPIO.HIGH)
        sleep(config.getfloat('shot', 'second'))
        _, frame=capture.read()
        cv2.imwrite(base_path + led_pos + '.png', frame)
        GPIO.output(pin_num, GPIO.LOW)
        if led_pos=='front' and kake(base_path + led_pos + '.png'):
            return 'kake'
            break
        result = dakon_kizu(base_path + led_pos + '.png')
        if result == 1:
            return 'dakon'
            break
        elif result == 2:
            return 'kizu'
            break
    capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

