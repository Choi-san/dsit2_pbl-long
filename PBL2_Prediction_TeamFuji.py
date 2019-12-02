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
from tensorflow.keras.models import load_model
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

class GPIO_led:
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.GPIO = GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.pin_num, self.GPIO.OUT)
        
    def led_on(self):
        self.GPIO.output(self.pin_num, self.GPIO.HIGH)

    def led_off(self):
        self.GPIO.output(self.pin_num, self.GPIO.LOW)

class camera:
    def __init__(self, width, height, fps=4):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3,width)
        self.cap.set(4,height)
        self.cap.set(5,fps) # FPS
    
    def realtime(self):
        while(self.cap.isOpened()):
            _, self.frame = self.cap.read()
            cv2.imshow('frame',self.frame)
            if cv2.waitKey(1) != -1:
                break
        return
    
    def shot(self):
        ret, self.frame = self.cap.read()
        return ret

    def pass_frame(self, num_frame):
        for i in range(num_frame):
            _, self.frame = self.cap.read()
        return

    def shot_and_save(self, name, cntr=0):
        if cntr>=5:
            print('check camera again...')
            return False
        
        ret, self.frame = self.cap.read()
        if ret:
            cv2.imwrite(name, self.frame)
            return True
        else:
            cntr+=1

        self.shot_and_save(self, name, cntr)
    
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

def pred():
    base_path = './pict/' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '/'
    dakon_kizu_model=load_model('./model/dakon_kizu_model.hdf5')
    os.makedirs(base_path, exist_ok=True)
    config = configparser.ConfigParser()
    config.read('./config.ini', 'utf_8')
    led_pos_list = ['front','right','left','back']
    width, height, fps = 224, 224, 30
    camera = camera(width, height, fps)

    for led_pos in led_pos_list:
        pin_num = config.getint('pin_number',led_pos)
        led = GPIO_led(pin_num)
        led.led_on()
        camera.pass_frame(int(fps * config.getfloat('shot', 'second') * 1.5))    # スリープさせる分、フレームを捨てる
        camera.shot_and_save(base_path + led_pos + '.png')
        led.led_off()

        expand2square(Image.open(base_path + led_pos + '.png'), (0, 0, 0)).resize((224, 224)).save(base_path + led_pos + '.png', quality=100)
        img = load_img(base_path + led_pos + '.png', target_size=(224, 224))
        x=img_to_array(img)
        
        if led_pos=='front' and kake(x):
            return 1
        result = dakon_kizu(x, dakon_kizu_model)
        if result == 0:   # dakon
            return 2
        elif result == 1:  # kizu
            return 3
        camera.pass_frame(int(fps * 1))    # 推論処理で必要となった時間（仮に1秒）分、フレームを捨てる
    return 0

if __name__ == '__main__':
    pred()

