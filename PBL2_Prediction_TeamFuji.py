# coding: utf-8
import os
import glob
import sys
import RPi.GPIO as GPIO
from time import sleep
import warnings
import cv2
import datetime
import configparser
from PIL import Image
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy  as np

warnings.simplefilter('ignore')

def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result

def kake(x):
    return 0

def dakon_kizu(x, model):
    classes = ['dakon', 'kizu', 'ok']
    return np.argmax(model.predict(x.reshape(1, x.shape[0], x.shape[1], x.shape[2])))

def pred():
    base_path = './pict/' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '/'
    dakon_kizu_model=load_model('./model/dakon_kizu_model.hdf5')
    os.makedirs(base_path, exist_ok=True)
    config = configparser.ConfigParser()
    config.read('./config.ini', 'utf_8')
    led_pos_list = ['front','right','left','back']
    GPIO.setmode(GPIO.BCM)

    for led_pos in led_pos_list:
        capture = cv2.VideoCapture(0)
        capture.set(3,224)
        capture.set(4,224)
        pin_num = config.getint('pin_number',led_pos)
        GPIO.setup(pin_num, GPIO.OUT)
        GPIO.output(pin_num, GPIO.HIGH)
        sleep(config.getfloat('shot', 'second'))
        _, frame=capture.read()
        cv2.imwrite(base_path + led_pos + '.png', frame)
        GPIO.output(pin_num, GPIO.LOW)
        capture.release()

        expand2square(Image.open(base_path + led_pos + '.png'), (0, 0, 0)).resize((224, 224)).save(base_path + led_pos + '.png', quality=100)
        img = load_img(base_path + led_pos + '.png', target_size=(224, 224))
        x=img_to_array(img)
        
        if led_pos=='front' and kake(x):
            return 1
            break
        result = dakon_kizu(x, dakon_kizu_model)
        if result == 0:   # dakon
            return 2
            break
        elif result == 1:  # kizu
            return 3
            break
    return 0

if __name__ == '__main__':
    pred()

